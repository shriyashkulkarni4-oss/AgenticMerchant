"""
Product ORM Model.

Represents a product listed by a merchant, with bargaining configuration.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.negotiation import NegotiationSession
    from app.models.order import Order


class Product(Base):
    """Product listing with negotiation settings.

    Attributes:
        id: Unique identifier (UUID).
        merchant_id: Foreign key to the owning merchant.
        name: Product name.
        description: Optional product description.
        price: Listed price.
        min_acceptable_price: Merchant's floor price for bargaining.
        auto_accept_threshold: Auto-accept offers at or above this price.
        bargaining_enabled: Whether bargaining is allowed for this product.
        max_negotiation_rounds: Maximum rounds of negotiation allowed.
        stock_quantity: Available stock quantity.
        category: Optional product category.
        tags: Optional list of tag strings (stored as JSON).
        image_url: Optional product image URL.
        is_active: Whether the product is currently listed.
        metadata_: Extra attributes from crawling (column name "metadata").
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("merchants.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    min_acceptable_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    auto_accept_threshold: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    bargaining_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    max_negotiation_rounds: Mapped[int] = mapped_column(
        Integer,
        default=5,
    )
    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    tags: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    metadata_: Mapped[Optional[Any]] = mapped_column(
        "metadata",
        JSON,
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
    merchant: Mapped[Merchant] = relationship(
        "Merchant",
        back_populates="products",
    )
    orders: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="product",
    )
    negotiation_sessions: Mapped[list[NegotiationSession]] = relationship(
        "NegotiationSession",
        back_populates="product",
    )
