"""
Merchant ORM Model.

Represents a merchant business account linked to a user.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.crawl import CrawlJob
    from app.models.order import Order
    from app.models.product import Product
    from app.models.user import User


class Merchant(Base):
    """Merchant business profile.

    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to the owning user account.
        business_name: Name of the merchant business.
        website_url: Optional URL of the merchant's website.
        description: Optional business description.
        is_active: Whether the merchant is currently active.
        crawl_status: Status of website crawling (pending/crawling/completed/failed).
        graphify_data_path: Path to the graphify output directory for this merchant.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    business_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    crawl_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
    )
    graphify_data_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped[User] = relationship(
        "User",
        back_populates="merchant",
    )
    products: Mapped[list[Product]] = relationship(
        "Product",
        back_populates="merchant",
    )
    orders: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="merchant",
    )
    crawl_jobs: Mapped[list[CrawlJob]] = relationship(
        "CrawlJob",
        back_populates="merchant",
    )
