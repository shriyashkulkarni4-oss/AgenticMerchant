"""
Order Pydantic Schemas.

Request and response schemas for order creation and status management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class OrderCreate(BaseModel):
    """Schema for creating a new order.

    Attributes:
        product_id: UUID of the product to order.
        quantity: Number of units to order.
        negotiation_session_id: Optional UUID of the negotiation session
            that determined the price.
    """

    product_id: UUID
    quantity: int = 1
    negotiation_session_id: Optional[UUID] = None


class OrderResponse(BaseModel):
    """Schema for order responses.

    Attributes:
        id: Order UUID.
        user_id: Buying user UUID.
        merchant_id: Selling merchant UUID.
        product_id: Product UUID.
        negotiation_session_id: Negotiation session UUID (if applicable).
        quantity: Number of units.
        unit_price: Price per unit.
        total_price: Total order price.
        original_price: Original listed price.
        status: Order status.
        created_at: Order creation timestamp.
        updated_at: Last update timestamp.
    """

    id: UUID
    user_id: UUID
    merchant_id: UUID
    product_id: UUID
    negotiation_session_id: Optional[UUID]
    quantity: int
    unit_price: float
    total_price: float
    original_price: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    product_name: Optional[str] = None
    merchant_name: Optional[str] = None
    buyer_name: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    """Schema for updating an order's status.

    Attributes:
        status: New status value (pending/confirmed/shipped/delivered/cancelled).
    """

    status: str
