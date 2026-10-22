"""
User ORM Model.

Represents application users with roles: merchant, consumer, or admin.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.negotiation import NegotiationSession
    from app.models.order import Order


class User(Base):
    """Application user account.

    Attributes:
        id: Unique identifier (UUID).
        email: User email address (unique, indexed).
        hashed_password: Bcrypt-hashed password.
        full_name: Display name.
        role: One of 'merchant', 'consumer', or 'admin'.
        is_active: Whether the account is active.
        created_at: Timestamp of account creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    merchant: Mapped[Optional[Merchant]] = relationship(
        "Merchant",
        back_populates="user",
        uselist=False,
    )
    orders: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="user",
    )
    negotiation_sessions: Mapped[list[NegotiationSession]] = relationship(
        "NegotiationSession",
        back_populates="user",
    )
