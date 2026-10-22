"""
Negotiation API Router for AgenticBuy.

Endpoints to initiate and advance price negotiations between consumers
and the autonomous AI bargaining agent according to merchant rules.
"""

from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.utils import get_current_user
from app.database import get_db
from app.models.negotiation import NegotiationMessage, NegotiationSession
from app.models.product import Product
from app.models.user import User
from app.schemas.negotiation import (
    NegotiationOffer,
    NegotiationSessionResponse,
    NegotiationStart,
)
from app.services.negotiation import (
    calculate_counter_offer,
    evaluate_offer,
    generate_negotiation_message,
)

router = APIRouter(prefix="/api/v1/negotiate", tags=["negotiation"])


@router.post(
    "/",
    response_model=NegotiationSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new negotiation session",
)
async def start_negotiation(
    payload: NegotiationStart,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationSessionResponse:
    """Start bargaining on a product with merchant-configured bounds."""
    # 1. Fetch product
    p_stmt = select(Product).where(Product.id == payload.product_id)
    p_res = await db.execute(p_stmt)
    product = p_res.scalars().first()

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or unavailable.",
        )

    if not product.bargaining_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bargaining is not enabled for this product. Listed price is firm.",
        )

    if product.stock_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is currently out of stock.",
        )

    list_price = float(product.price)
    min_price = float(product.min_acceptable_price or list_price)
    auto_accept = float(product.auto_accept_threshold or list_price)
    offered = float(payload.offered_price)

    # 2. Evaluate opening offer
    action = evaluate_offer(
        offer=offered,
        min_price=min_price,
        auto_accept=auto_accept,
        list_price=list_price,
    )

    session_status = "active"
    counter_val = None
    final_price_val = None

    if action == "accept":
        session_status = "accepted"
        final_price_val = offered
        agent_msg = generate_negotiation_message(
            "accept",
            counter_offer=offered,
            product_name=product.name,
        )
    elif action == "reject":
        session_status = "rejected"
        agent_msg = generate_negotiation_message(
            "reject",
            product_name=product.name,
        )
    else:
        counter_val = calculate_counter_offer(
            current_offer=offered,
            list_price=list_price,
            min_price=min_price,
            round_num=1,
            max_rounds=product.max_negotiation_rounds,
        )
        agent_msg = generate_negotiation_message(
            "counter",
            counter_offer=counter_val,
            product_name=product.name,
            round_num=1,
        )

    # 3. Create Session
    session = NegotiationSession(
        product_id=product.id,
        user_id=current_user.id,
        status=session_status,
        initial_ask_price=offered,
        current_offer=offered,
        counter_offer=counter_val,
        final_price=final_price_val,
        rounds_used=1,
        max_rounds=product.max_negotiation_rounds,
    )
    db.add(session)
    await db.flush()

    # 4. Record user opening message
    user_opening = payload.message or f"I would like to offer ${offered:.2f} for {product.name}."
    user_message = NegotiationMessage(
        session_id=session.id,
        role="user",
        message=user_opening,
        offer_amount=offered,
    )
    db.add(user_message)

    # 5. Record agent reply message
    agent_message = NegotiationMessage(
        session_id=session.id,
        role="agent",
        message=agent_msg,
        offer_amount=counter_val or final_price_val,
    )
    db.add(agent_message)

    await db.commit()

    # Re-fetch with messages
    stmt = (
        select(NegotiationSession)
        .options(selectinload(NegotiationSession.messages))
        .where(NegotiationSession.id == session.id)
    )
    res = await db.execute(stmt)
    return res.scalars().first()


@router.get(
    "/{session_id}",
    response_model=NegotiationSessionResponse,
    summary="Get negotiation session details and message history",
)
async def get_negotiation_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationSessionResponse:
    """Retrieve an active or completed negotiation session."""
    stmt = (
        select(NegotiationSession)
        .options(selectinload(NegotiationSession.messages))
        .where(NegotiationSession.id == session_id)
    )
    result = await db.execute(stmt)
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation session not found",
        )

    if session.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden to this negotiation session.",
        )

    return session


@router.put(
    "/{session_id}",
    response_model=NegotiationSessionResponse,
    summary="Submit counter-offer or advance negotiation",
)
async def advance_negotiation(
    session_id: uuid.UUID,
    payload: NegotiationOffer,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationSessionResponse:
    """Submit a counter-offer in an active negotiation session."""
    stmt = (
        select(NegotiationSession)
        .options(selectinload(NegotiationSession.messages))
        .where(NegotiationSession.id == session_id)
    )
    res = await db.execute(stmt)
    session = res.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation session not found",
        )

    if session.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden to this negotiation session.",
        )

    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Negotiation session is already {session.status}.",
        )

    p_stmt = select(Product).where(Product.id == session.product_id)
    p_res = await db.execute(p_stmt)
    product = p_res.scalars().first()

    list_price = float(product.price)
    min_price = float(product.min_acceptable_price or list_price)
    auto_accept = float(product.auto_accept_threshold or list_price)
    offered = float(payload.offer_amount)

    session.rounds_used += 1
    session.current_offer = offered

    # Record buyer message
    buyer_msg = payload.message or f"How about ${offered:.2f}?"
    db.add(
        NegotiationMessage(
            session_id=session.id,
            role="user",
            message=buyer_msg,
            offer_amount=offered,
        )
    )

    if offered >= auto_accept:
        session.status = "accepted"
        session.final_price = offered
        agent_msg = generate_negotiation_message("accept", counter_offer=offered, product_name=product.name)
        db.add(NegotiationMessage(session_id=session.id, role="agent", message=agent_msg, offer_amount=offered))
    elif offered < min_price and session.rounds_used >= session.max_rounds:
        session.status = "rejected"
        agent_msg = generate_negotiation_message("reject", product_name=product.name)
        db.add(NegotiationMessage(session_id=session.id, role="agent", message=agent_msg, offer_amount=None))
    elif session.rounds_used >= session.max_rounds:
        # Final round take-it-or-leave-it
        session.counter_offer = min_price
        agent_msg = generate_negotiation_message("final_offer", counter_offer=min_price, product_name=product.name)
        db.add(NegotiationMessage(session_id=session.id, role="agent", message=agent_msg, offer_amount=min_price))
    else:
        counter_val = calculate_counter_offer(
            current_offer=offered,
            list_price=list_price,
            min_price=min_price,
            round_num=session.rounds_used,
            max_rounds=session.max_rounds,
        )
        session.counter_offer = counter_val
        agent_msg = generate_negotiation_message(
            "counter",
            counter_offer=counter_val,
            product_name=product.name,
            round_num=session.rounds_used,
        )
        db.add(NegotiationMessage(session_id=session.id, role="agent", message=agent_msg, offer_amount=counter_val))

    await db.commit()

    # Re-fetch updated
    stmt_updated = (
        select(NegotiationSession)
        .options(selectinload(NegotiationSession.messages))
        .where(NegotiationSession.id == session_id)
    )
    result = await db.execute(stmt_updated)
    return result.scalars().first()
