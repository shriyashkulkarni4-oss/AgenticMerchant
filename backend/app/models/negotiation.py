"""
Negotiation ORM Models.

Provides NegotiationSession and NegotiationMessage models for managing
price negotiations between consumers and the AI bargaining agent.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product
    from app.models.user import User


class NegotiationSession(Base):
    """A negotiation session between a user and the AI bargaining agent.

    Tracks the lifecycle of a price negotiation from initial offer
    through acceptance, rejection, or expiration.

    Attributes:
        id: Unique identifier (UUID).
        product_id: Foreign key to the product being negotiated.
        user_id: Foreign key to the user initiating the negotiation.
        status: Current status (active/accepted/rejected/expired).
        initial_ask_price: The user's first offered price.
        current_offer: The latest offer from the user.
        counter_offer: The latest counter-offer from the agent.
        final_price: The agreed-upon price (if accepted).
        rounds_used: Number of negotiation rounds completed.
        max_rounds: Maximum rounds allowed for this session.
        created_at: Timestamp of session creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "negotiation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
    )
    initial_ask_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    current_offer: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    counter_offer: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    final_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    rounds_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    max_rounds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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
    product: Mapped[Product] = relationship(
        "Product",
        back_populates="negotiation_sessions",
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="negotiation_sessions",
    )
    messages: Mapped[list[NegotiationMessage]] = relationship(
        "NegotiationMessage",
        back_populates="session",
    )
    order: Mapped[Optional[Order]] = relationship(
        "Order",
        back_populates="negotiation_session",
        uselist=False,
    )


class NegotiationMessage(Base):
    """A single message within a negotiation session.

    Attributes:
        id: Unique identifier (UUID).
        session_id: Foreign key to the parent negotiation session.
        role: Who sent the message — 'user' or 'agent'.
        message: The text content of the message.
        offer_amount: Optional monetary offer included in the message.
        created_at: Timestamp of when the message was sent.
    """

    __tablename__ = "negotiation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("negotiation_sessions.id"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    offer_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    # Relationships
    session: Mapped[NegotiationSession] = relationship(
        "NegotiationSession",
        back_populates="messages",
    )
