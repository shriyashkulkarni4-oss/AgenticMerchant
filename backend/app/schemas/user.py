"""
User Pydantic Schemas.

Request and response schemas for user registration, login, and profile.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user account."""

    email: EmailStr
    password: str
    full_name: str
    role: str = "consumer"
    business_name: Optional[str] = None
    website_url: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login credentials."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user profile responses."""

    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    merchant_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT authentication token response with user metadata."""

    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: UUID
    full_name: str
    merchant_id: Optional[UUID] = None
