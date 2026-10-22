"""
Merchant Pydantic Schemas.

Request and response schemas for merchant CRUD operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.product import ProductResponse


class MerchantCreate(BaseModel):
    """Schema for creating a new merchant profile.

    Attributes:
        business_name: Name of the business.
        website_url: Optional URL of the merchant's website.
        description: Optional business description.
    """

    business_name: str
    website_url: Optional[str] = None
    description: Optional[str] = None


class MerchantUpdate(BaseModel):
    """Schema for updating a merchant profile.

    All fields are optional; only provided fields are updated.

    Attributes:
        business_name: Updated business name.
        website_url: Updated website URL.
        description: Updated description.
        is_active: Updated active status.
    """

    business_name: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MerchantResponse(BaseModel):
    """Schema for merchant profile responses.

    Attributes:
        id: Merchant UUID.
        user_id: Owning user UUID.
        business_name: Business name.
        website_url: Website URL.
        description: Business description.
        is_active: Whether the merchant is active.
        crawl_status: Website crawl status.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: UUID
    user_id: UUID
    business_name: str
    website_url: Optional[str]
    description: Optional[str]
    is_active: bool
    crawl_status: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MerchantWithProducts(MerchantResponse):
    """Merchant response that includes the merchant's product listings.

    Attributes:
        products: List of products belonging to this merchant.
    """

    products: list[ProductResponse] = []
