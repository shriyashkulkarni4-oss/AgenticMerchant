"""
Product Pydantic Schemas.

Request and response schemas for product CRUD and search operations.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ProductCreate(BaseModel):
    """Schema for creating a new product listing.

    Attributes:
        name: Product name.
        description: Optional product description.
        price: Listed price.
        min_acceptable_price: Merchant's floor price for bargaining.
        auto_accept_threshold: Auto-accept offers at or above this price.
        bargaining_enabled: Whether bargaining is allowed.
        max_negotiation_rounds: Maximum negotiation rounds.
        stock_quantity: Available stock.
        category: Optional product category.
        tags: Optional list of tag strings.
        image_url: Optional product image URL.
        metadata_: Optional extra attributes from crawling.
    """

    name: str
    description: Optional[str] = None
    price: float
    min_acceptable_price: Optional[float] = None
    auto_accept_threshold: Optional[float] = None
    bargaining_enabled: bool = True
    max_negotiation_rounds: int = 5
    stock_quantity: int = 0
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    image_url: Optional[str] = None
    metadata_: Optional[dict[str, Any]] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product listing.

    All fields are optional; only provided fields are updated.

    Attributes:
        name: Updated product name.
        description: Updated description.
        price: Updated price.
        min_acceptable_price: Updated floor price.
        auto_accept_threshold: Updated auto-accept threshold.
        bargaining_enabled: Updated bargaining flag.
        max_negotiation_rounds: Updated max rounds.
        stock_quantity: Updated stock.
        category: Updated category.
        tags: Updated tags.
        image_url: Updated image URL.
        metadata_: Updated extra attributes.
        is_active: Updated active status.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    min_acceptable_price: Optional[float] = None
    auto_accept_threshold: Optional[float] = None
    bargaining_enabled: Optional[bool] = None
    max_negotiation_rounds: Optional[int] = None
    stock_quantity: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    image_url: Optional[str] = None
    metadata_: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema for product listing responses.

    Attributes:
        id: Product UUID.
        merchant_id: Owning merchant UUID.
        name: Product name.
        description: Product description.
        price: Listed price.
        min_acceptable_price: Floor price.
        auto_accept_threshold: Auto-accept threshold.
        bargaining_enabled: Whether bargaining is allowed.
        max_negotiation_rounds: Max negotiation rounds.
        stock_quantity: Available stock.
        category: Product category.
        tags: Tag strings.
        image_url: Product image URL.
        is_active: Whether the product is listed.
        metadata_: Extra crawl attributes.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: UUID
    merchant_id: UUID
    name: str
    description: Optional[str]
    price: float
    min_acceptable_price: Optional[float]
    auto_accept_threshold: Optional[float]
    bargaining_enabled: bool
    max_negotiation_rounds: int
    stock_quantity: int
    category: Optional[str]
    tags: Optional[list[str]]
    image_url: Optional[str]
    is_active: bool
    metadata_: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ProductSearch(BaseModel):
    """Schema for product search / filter parameters.

    Attributes:
        query: Free-text search query.
        category: Filter by category.
        min_price: Minimum price filter.
        max_price: Maximum price filter.
        merchant_id: Filter by merchant UUID.
        tags: Filter by tags.
        limit: Maximum results to return.
        offset: Pagination offset.
    """

    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    merchant_id: Optional[UUID] = None
    tags: Optional[list[str]] = None
    limit: int = 20
    offset: int = 0
