"""Core news fetching engine - fetches and parses RSS feeds concurrently."""

from __future__ import annotations

import asyncio
import html
import re
from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx

from newsgraber.config import get_settings
from newsgraber.models import Article, Category, FetchResult, NewsSource


def _clean_html(text: str) -> str:
    """Strip HTML tags and decode entities from a string."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_date(entry: dict) -> datetime | None:
    """Extract published date from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None) if hasattr(entry, attr) else entry.get(attr)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except (ValueError, OverflowError):
                continue
    return None


def _extract_image(entry: dict) -> str:
    """Try to extract an image URL from the entry."""
    # media:thumbnail
    media = entry.get("media_thumbnail", [])
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]

    # media:content
    media_content = entry.get("media_content", [])
    if media_content and isinstance(media_content, list):
        for m in media_content:
            if m.get("medium") == "image" and m.get("url"):
                return m["url"]

    # enclosure
    enclosures = entry.get("enclosures", [])
    if enclosures:
        for enc in enclosures:
            if enc.get("type", "").startswith("image/") and enc.get("href"):
                return enc["href"]

    return ""


def _parse_feed(feed_data: str, source: NewsSource, max_items: int) -> list[Article]:
    """Parse RSS feed content into Article objects."""
    parsed = feedparser.parse(feed_data)
    articles: list[Article] = []

    for entry in parsed.entries[:max_items]:
        title = _clean_html(entry.get("title", ""))
        if not title:
            continue

        link = entry.get("link", "")
        summary = _clean_html(entry.get("summary", "") or entry.get("description", ""))
        if len(summary) > 500:
            summary = summary[:497] + "..."

        articles.append(
            Article(
                title=title,
                link=link,
                summary=summary,
                source_id=source.id,
                source_name=source.name,
                published=_parse_date(entry),
                category=source.category,
                language=source.language,
                image_url=_extract_image(entry),
            )
        )

    return articles


async def fetch_source(
    client: httpx.AsyncClient,
    source: NewsSource,
    max_items: int,
) -> tuple[list[Article], FetchResult]:
    """Fetch and parse a single RSS source."""
    try:
        response = await client.get(source.url, follow_redirects=True)
        response.raise_for_status()
        articles = _parse_feed(response.text, source, max_items)
        return articles, FetchResult(
            source_id=source.id,
            source_name=source.name,
            success=True,
            article_count=len(articles),
        )
    except Exception as exc:
        return [], FetchResult(
            source_id=source.id,
            source_name=source.name,
            success=False,
            error=str(exc),
        )


async def fetch_all(
    sources: list[NewsSource],
    language: str = "",
) -> tuple[list[Article], list[FetchResult]]:
    """Fetch news from all provided sources concurrently.

    Args:
        sources: List of news sources to fetch.
        language: Filter to only sources matching this language code (empty = all).

    Returns:
        Tuple of (all_articles, fetch_results).
    """
    settings = get_settings()

    if language:
        sources = [s for s in sources if s.language == language]

    semaphore = asyncio.Semaphore(settings.fetch_concurrency)

    async def _limited_fetch(
        client: httpx.AsyncClient, source: NewsSource
    ) -> tuple[list[Article], FetchResult]:
        async with semaphore:
            return await fetch_source(client, source, settings.max_articles_per_source)

    all_articles: list[Article] = []
    all_results: list[FetchResult] = []

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(settings.fetch_timeout),
        headers={"User-Agent": settings.user_agent},
    ) as client:
        tasks = [_limited_fetch(client, source) for source in sources]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for item in completed:
            if isinstance(item, Exception):
                continue
            articles, result = item
            all_articles.extend(articles)
            all_results.append(result)

    # Sort by published date (newest first), fallback to fetched_at
    all_articles.sort(
        key=lambda a: a.published or a.fetched_at,
        reverse=True,
    )

    return all_articles, all_results
