"""
Merchant API Router for AgenticBuy.

Endpoints for merchant onboarding, profile management, and merchant listings.
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.utils import get_current_user
from app.database import get_db
from app.models.merchant import Merchant
from app.models.user import User
from app.schemas.merchant import (
    MerchantCreate,
    MerchantResponse,
    MerchantUpdate,
    MerchantWithProducts,
)

router = APIRouter(prefix="/api/v1/merchants", tags=["merchants"])


@router.post(
    "/",
    response_model=MerchantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register/Create merchant profile",
)
async def create_merchant(
    payload: MerchantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MerchantResponse:
    """Create a new merchant profile linked to the authenticated user account."""
    if current_user.role != "merchant" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with merchant role can register a merchant profile.",
        )

    # Check if this user already has a merchant profile
    existing_stmt = select(Merchant).where(Merchant.user_id == current_user.id)
    result = await db.execute(existing_stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A merchant profile already exists for this user.",
        )

    merchant = Merchant(
        user_id=current_user.id,
        business_name=payload.business_name,
        website_url=str(payload.website_url) if payload.website_url else None,
        description=payload.description,
        is_active=True,
        crawl_status="pending",
    )
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    return merchant


@router.get(
    "/",
    response_model=List[MerchantResponse],
    summary="List all merchants",
)
async def list_merchants(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> List[MerchantResponse]:
    """Retrieve all merchants with optional pagination."""
    stmt = select(Merchant)
    if active_only:
        stmt = stmt.where(Merchant.is_active == True)  # noqa: E712
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get(
    "/{merchant_id}",
    response_model=MerchantWithProducts,
    summary="Get merchant details with products",
)
async def get_merchant(
    merchant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MerchantWithProducts:
    """Retrieve detailed information about a merchant including listed products."""
    stmt = (
        select(Merchant)
        .options(selectinload(Merchant.products))
        .where(Merchant.id == merchant_id)
    )
    result = await db.execute(stmt)
    merchant = result.scalars().first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )
    return merchant


@router.put(
    "/{merchant_id}",
    response_model=MerchantResponse,
    summary="Update merchant details",
)
async def update_merchant(
    merchant_id: uuid.UUID,
    payload: MerchantUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MerchantResponse:
    """Update merchant profile. Caller must be the merchant owner or admin."""
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalars().first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    if merchant.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this merchant profile.",
        )

    if payload.business_name is not None:
        merchant.business_name = payload.business_name
    if payload.website_url is not None:
        merchant.website_url = str(payload.website_url)
    if payload.description is not None:
        merchant.description = payload.description
    if payload.is_active is not None:
        merchant.is_active = payload.is_active

    await db.commit()
    await db.refresh(merchant)
    return merchant


@router.delete(
    "/{merchant_id}",
    response_model=MerchantResponse,
    summary="Deactivate merchant profile",
)
async def delete_merchant(
    merchant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MerchantResponse:
    """Soft delete (deactivate) a merchant profile."""
    stmt = select(Merchant).where(Merchant.id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalars().first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    if merchant.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to deactivate this merchant.",
        )

    merchant.is_active = False
    await db.commit()
    await db.refresh(merchant)
    return merchant
