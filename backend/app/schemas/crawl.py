"""
Crawl Pydantic Schemas for AgenticBuy.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class CrawlStartRequest(BaseModel):
    """Schema for requesting a merchant website crawl."""

    url: HttpUrl
    max_pages: int = 30


class CrawlJobResponse(BaseModel):
    """Schema for crawl job status response."""

    id: UUID
    merchant_id: UUID
    url: str
    status: str
    result: Optional[Any] = None
    error_message: Optional[str] = None
    pages_crawled: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
