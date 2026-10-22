"""
Order API Router for AgenticBuy.

Endpoints for placing purchases (at listed price or negotiated price)
and tracking fulfillment status.
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import get_current_user, get_optional_current_user
from app.database import get_db
from app.models.merchant import Merchant
from app.models.negotiation import NegotiationSession
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place a product order",
)
async def create_order(
    payload: OrderCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Place an order for a product at listed price or an agreed negotiated price."""
    # If unauthenticated, find default consumer
    user = current_user
    if not user:
        u_res = await db.execute(select(User).where(User.role == "consumer").limit(1))
        user = u_res.scalars().first()
        if not user:
            u_res = await db.execute(select(User).limit(1))
            user = u_res.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to place an order.",
            )

    # 1. Fetch product
    p_stmt = select(Product).where(Product.id == payload.product_id)
    p_res = await db.execute(p_stmt)
    product = p_res.scalars().first()

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or unavailable.",
        )

    if product.stock_quantity < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock_quantity}, requested: {payload.quantity}.",
        )

    unit_price = float(product.price)
    original_price = float(product.price)

    # 2. Check negotiation session if provided
    if payload.negotiation_session_id:
        n_stmt = select(NegotiationSession).where(
            NegotiationSession.id == payload.negotiation_session_id
        )
        n_res = await db.execute(n_stmt)
        neg_session = n_res.scalars().first()

        if not neg_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negotiation session not found.",
            )

        if neg_session.status != "accepted" or not neg_session.final_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Negotiation session was not successfully accepted.",
            )

        unit_price = float(neg_session.final_price)

    total_price = unit_price * payload.quantity

    # 3. Decrement stock
    product.stock_quantity -= payload.quantity

    # 4. Create Order
    order = Order(
        user_id=user.id,
        merchant_id=product.merchant_id,
        product_id=product.id,
        negotiation_session_id=payload.negotiation_session_id,
        quantity=payload.quantity,
        unit_price=unit_price,
        total_price=total_price,
        original_price=original_price,
        status="confirmed",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Load merchant and user info for response
    m_res = await db.execute(select(Merchant).where(Merchant.id == product.merchant_id))
    merch = m_res.scalars().first()

    resp = OrderResponse.model_validate(order)
    resp.product_name = product.name
    resp.merchant_name = merch.business_name if merch else "Merchant"
    resp.buyer_name = user.full_name or user.email
    return resp


@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="List orders for current user or merchant",
)
async def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OrderResponse]:
    """Retrieve orders relevant to the current user (as buyer or merchant)."""
    stmt = (
        select(Order)
        .options(
            selectinload(Order.product),
            selectinload(Order.merchant),
            selectinload(Order.user),
        )
    )

    if current_user:
        if current_user.role == "merchant":
            m_stmt = select(Merchant).where(Merchant.user_id == current_user.id)
            m_res = await db.execute(m_stmt)
            merchant = m_res.scalars().first()
            if merchant:
                stmt = stmt.where(Order.merchant_id == merchant.id)
            else:
                stmt = stmt.where(Order.user_id == current_user.id)
        elif current_user.role == "consumer":
            stmt = stmt.where(Order.user_id == current_user.id)

    if status_filter:
        stmt = stmt.where(Order.status == status_filter)

    stmt = stmt.order_by(Order.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    orders = list(result.scalars().all())

    responses = []
    for o in orders:
        item = OrderResponse.model_validate(o)
        item.product_name = o.product.name if o.product else "Product"
        item.merchant_name = o.merchant.business_name if o.merchant else "Merchant Store"
        item.buyer_name = o.user.full_name or o.user.email if o.user else "Consumer"
        responses.append(item)

    return responses


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Get single order details by ID."""
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Allow buyer or selling merchant or admin
    if order.user_id != current_user.id and current_user.role != "admin":
        m_stmt = select(Merchant).where(Merchant.user_id == current_user.id)
        m_res = await db.execute(m_stmt)
        merchant = m_res.scalars().first()
        if not merchant or merchant.id != order.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order.",
            )

    return order


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order fulfillment status",
)
async def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Update order fulfillment status (merchant or admin)."""
    valid_statuses = {"pending", "confirmed", "shipped", "delivered", "cancelled"}
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Verify merchant ownership
    if current_user.role != "admin":
        m_stmt = select(Merchant).where(Merchant.user_id == current_user.id)
        m_res = await db.execute(m_stmt)
        merchant = m_res.scalars().first()
        if not merchant or merchant.id != order.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order.",
            )

    order.status = payload.status
    await db.commit()
    await db.refresh(order)
    return order
