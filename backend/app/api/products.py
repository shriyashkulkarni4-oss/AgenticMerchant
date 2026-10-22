"""
Product API Router for AgenticBuy.

Endpoints for product catalog management, retrieval, filtering, and semantic search.
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import get_current_user
from app.database import get_chroma_client, get_db
from app.models.merchant import Merchant
from app.models.product import Product
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductSearch,
    ProductUpdate,
)
from app.services.embeddings import search_products as chroma_search

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product listing",
)
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Create a new product under the authenticated user's merchant profile."""
    # Find merchant profile for current user
    stmt = select(Merchant).where(Merchant.user_id == current_user.id)
    result = await db.execute(stmt)
    merchant = result.scalars().first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user does not have an active merchant profile. Please register as a merchant first.",
        )

    product = Product(
        merchant_id=merchant.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        min_acceptable_price=payload.min_acceptable_price,
        auto_accept_threshold=payload.auto_accept_threshold,
        bargaining_enabled=payload.bargaining_enabled,
        max_negotiation_rounds=payload.max_negotiation_rounds,
        stock_quantity=payload.stock_quantity,
        category=payload.category,
        tags=payload.tags,
        image_url=str(payload.image_url) if payload.image_url else None,
        metadata_=payload.metadata_,
        is_active=True,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="List and filter products",
)
async def list_products(
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    merchant_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
) -> List[ProductResponse]:
    """Retrieve products with optional filtering by category, price, merchant, or keywords."""
    stmt = select(Product)

    if active_only:
        stmt = stmt.where(Product.is_active == True)  # noqa: E712
    if category:
        stmt = stmt.where(Product.category == category)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
    if merchant_id:
        stmt = stmt.where(Product.merchant_id == merchant_id)
    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
            )
        )

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get(
    "/mine",
    response_model=List[ProductResponse],
    summary="Get current merchant's products",
)
async def get_my_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProductResponse]:
    """Retrieve all products belonging to the authenticated merchant."""
    m_stmt = select(Merchant).where(Merchant.user_id == current_user.id)
    m_res = await db.execute(m_stmt)
    merchant = m_res.scalars().first()
    if not merchant:
        return []

    stmt = (
        select(Product)
        .where(Product.merchant_id == merchant.id, Product.is_active == True)  # noqa: E712
        .order_by(Product.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product detail",
)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Retrieve full details of a specific product."""
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product listing",
)
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Update a product listing. Only the owning merchant or admin can update."""
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Verify ownership
    merchant_stmt = select(Merchant).where(Merchant.id == product.merchant_id)
    m_res = await db.execute(merchant_stmt)
    merchant = m_res.scalars().first()

    if (
        not merchant
        or (merchant.user_id != current_user.id and current_user.role != "admin")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this product.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "image_url" and value:
            setattr(product, field, str(value))
        else:
            setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Deactivate product listing",
)
async def delete_product(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Soft delete (deactivate) a product listing."""
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    merchant_stmt = select(Merchant).where(Merchant.id == product.merchant_id)
    m_res = await db.execute(merchant_stmt)
    merchant = m_res.scalars().first()

    if (
        not merchant
        or (merchant.user_id != current_user.id and current_user.role != "admin")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to deactivate this product.",
        )

    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return product


@router.post(
    "/search",
    response_model=List[ProductResponse],
    summary="Semantic or hybrid product search",
)
async def search_products(
    payload: ProductSearch,
    db: AsyncSession = Depends(get_db),
) -> List[ProductResponse]:
    """Semantic vector search across products with fallback to SQL text search."""
    matched_ids: list[uuid.UUID] = []

    # Attempt ChromaDB semantic vector search if query text is provided
    if payload.query:
        try:
            client = get_chroma_client()
            results = await chroma_search(
                query=payload.query,
                chroma_client=client,
                limit=payload.limit,
            )
            for r in results:
                try:
                    matched_ids.append(uuid.UUID(r["id"]))
                except (ValueError, KeyError):
                    continue
        except Exception:
            # Fallback gracefully to standard SQL filtering if ChromaDB/embeddings are unavailable
            matched_ids = []

    stmt = select(Product).where(Product.is_active == True)  # noqa: E712

    if matched_ids:
        stmt = stmt.where(Product.id.in_(matched_ids))
    elif payload.query:
        query_pattern = f"%{payload.query}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(query_pattern),
                Product.description.ilike(query_pattern),
            )
        )

    if payload.category:
        stmt = stmt.where(Product.category == payload.category)
    if payload.min_price is not None:
        stmt = stmt.where(Product.price >= payload.min_price)
    if payload.max_price is not None:
        stmt = stmt.where(Product.price <= payload.max_price)
    if payload.merchant_id:
        stmt = stmt.where(Product.merchant_id == payload.merchant_id)

    stmt = stmt.offset(payload.offset).limit(payload.limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
