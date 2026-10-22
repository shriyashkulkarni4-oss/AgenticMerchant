"""
CrawlJob ORM Model.

Tracks website crawling jobs for merchant product ingestion.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant


class CrawlJob(Base):
    """A web crawling job for a merchant's website.

    Attributes:
        id: Unique identifier (UUID).
        merchant_id: Foreign key to the merchant whose site is being crawled.
        url: The URL being crawled.
        status: Job status (pending/running/completed/failed).
        result: JSON summary of crawl results.
        error_message: Error details if the crawl failed.
        pages_crawled: Number of pages successfully crawled.
        created_at: Timestamp of job creation.
        completed_at: Timestamp of job completion.
    """

    __tablename__ = "crawl_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("merchants.id"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
    )
    result: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    pages_crawled: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Relationships
    merchant: Mapped[Merchant] = relationship(
        "Merchant",
        back_populates="crawl_jobs",
    )
