"""
Order ORM Model.

Represents a purchase order, optionally linked to a negotiation session.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.negotiation import NegotiationSession
    from app.models.product import Product
    from app.models.user import User


class Order(Base):
    """A purchase order for a product.

    Attributes:
        id: Unique identifier (UUID).
        user_id: Foreign key to the buying user.
        merchant_id: Foreign key to the selling merchant.
        product_id: Foreign key to the purchased product.
        negotiation_session_id: Optional foreign key to the negotiation
            session that determined the final price.
        quantity: Number of units ordered.
        unit_price: Price per unit (may be negotiated).
        total_price: Total order price (unit_price * quantity).
        original_price: Original listed price before negotiation.
        status: Order status (pending/confirmed/shipped/delivered/cancelled).
        created_at: Timestamp of order creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("merchants.id"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    negotiation_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("negotiation_sessions.id"),
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    original_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
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
        back_populates="orders",
    )
    merchant: Mapped[Merchant] = relationship(
        "Merchant",
        back_populates="orders",
    )
    product: Mapped[Product] = relationship(
        "Product",
        back_populates="orders",
    )
    negotiation_session: Mapped[Optional[NegotiationSession]] = relationship(
        "NegotiationSession",
        back_populates="order",
    )
