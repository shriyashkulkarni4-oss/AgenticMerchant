"""
Negotiation Pydantic Schemas.

Request and response schemas for negotiation sessions and messages.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NegotiationStart(BaseModel):
    """Schema for initiating a new negotiation session.

    Attributes:
        product_id: UUID of the product to negotiate on.
        offered_price: The user's initial price offer.
        message: Optional opening message.
    """

    product_id: UUID
    offered_price: float
    message: Optional[str] = None


class NegotiationOffer(BaseModel):
    """Schema for submitting a new offer within an active session.

    Attributes:
        offer_amount: The user's new price offer.
        message: Optional message accompanying the offer.
    """

    offer_amount: float
    message: Optional[str] = None


class NegotiationMessageResponse(BaseModel):
    """Schema for a single negotiation message response.

    Attributes:
        id: Message UUID.
        session_id: Parent session UUID.
        role: Sender role — 'user' or 'agent'.
        message: Message text content.
        offer_amount: Monetary offer included in the message.
        created_at: Timestamp of the message.
    """

    id: UUID
    session_id: UUID
    role: str
    message: str
    offer_amount: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class NegotiationSessionResponse(BaseModel):
    """Schema for a full negotiation session response.

    Attributes:
        id: Session UUID.
        product_id: Product UUID.
        user_id: User UUID.
        status: Session status (active/accepted/rejected/expired).
        current_offer: Latest user offer.
        counter_offer: Latest agent counter-offer.
        final_price: Agreed price (if accepted).
        rounds_used: Number of rounds completed.
        max_rounds: Maximum rounds allowed.
        messages: List of messages in this session.
        created_at: Session creation timestamp.
    """

    id: UUID
    product_id: UUID
    user_id: UUID
    status: str
    current_offer: Optional[float]
    counter_offer: Optional[float]
    final_price: Optional[float]
    rounds_used: int
    max_rounds: int
    messages: list[NegotiationMessageResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
