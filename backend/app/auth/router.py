"""
Authentication Router for AgenticBuy.

Provides endpoints for user and merchant registration, login, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.merchant import Merchant
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Register a new user or merchant account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create the user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    merchant_id = None
    if user_data.role == "merchant":
        b_name = user_data.business_name or f"{user_data.full_name}'s Store"
        merchant = Merchant(
            user_id=user.id,
            business_name=b_name,
            website_url=str(user_data.website_url) if user_data.website_url else None,
            description=f"Storefront for {b_name}",
            is_active=True,
            crawl_status="pending",
        )
        db.add(merchant)
        await db.flush()
        merchant_id = merchant.id

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        merchant_id=merchant_id,
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Authenticate a user or merchant and return a JWT token with profile info."""
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    merchant_id = None
    if user.role == "merchant":
        m_res = await db.execute(select(Merchant).where(Merchant.user_id == user.id))
        merchant = m_res.scalars().first()
        if merchant:
            merchant_id = merchant.id

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        merchant_id=merchant_id,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get the current authenticated user's profile."""
    merchant_id = None
    if current_user.role == "merchant":
        m_res = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
        merchant = m_res.scalars().first()
        if merchant:
            merchant_id = merchant.id

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        merchant_id=merchant_id,
    )
