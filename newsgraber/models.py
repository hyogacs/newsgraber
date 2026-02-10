"""Data models for news articles and sources."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    WORLD = "world"
    POLITICS = "politics"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    HEALTH = "health"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    GENERAL = "general"


class NewsSource(BaseModel):
    """Configuration for a single RSS news source."""

    id: str
    name: str
    url: str
    language: str = "en"
    category: Category = Category.GENERAL
    country: str = ""


class Article(BaseModel):
    """A single news article."""

    title: str
    link: str
    summary: str = ""
    source_id: str
    source_name: str
    published: datetime | None = None
    category: Category = Category.GENERAL
    language: str = "en"
    image_url: str = ""
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def display_time(self) -> str:
        if self.published:
            return self.published.strftime("%Y-%m-%d %H:%M")
        return self.fetched_at.strftime("%Y-%m-%d %H:%M")


class FetchResult(BaseModel):
    """Result of fetching from a single source."""

    source_id: str
    source_name: str
    success: bool
    article_count: int = 0
    error: str = ""
