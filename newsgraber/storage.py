"""SQLite storage layer for persisting fetched articles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from newsgraber.config import get_settings
from newsgraber.models import Article, Category

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    summary TEXT DEFAULT '',
    source_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    published TEXT,
    category TEXT DEFAULT 'general',
    language TEXT DEFAULT 'en',
    image_url TEXT DEFAULT '',
    fetched_at TEXT NOT NULL
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_id);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_fetched ON articles(fetched_at DESC);
"""


def _db_path() -> str:
    return get_settings().db_path


async def init_db(db_path: str | None = None) -> None:
    """Initialize the database schema."""
    path = db_path or _db_path()
    async with aiosqlite.connect(path) as db:
        await db.execute(_CREATE_TABLE)
        await db.executescript(_CREATE_INDEX)
        await db.commit()


async def save_articles(articles: list[Article], db_path: str | None = None) -> int:
    """Save articles to the database, skipping duplicates by link. Returns count saved."""
    path = db_path or _db_path()
    saved = 0
    async with aiosqlite.connect(path) as db:
        for article in articles:
            try:
                await db.execute(
                    """INSERT OR IGNORE INTO articles
                       (title, link, summary, source_id, source_name, published,
                        category, language, image_url, fetched_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        article.title,
                        article.link,
                        article.summary,
                        article.source_id,
                        article.source_name,
                        article.published.isoformat() if article.published else None,
                        article.category.value,
                        article.language,
                        article.image_url,
                        article.fetched_at.isoformat(),
                    ),
                )
                if db.total_changes:
                    saved += 1
            except Exception:
                continue
        await db.commit()
    return saved


def _row_to_article(row: aiosqlite.Row) -> Article:
    """Convert a database row to an Article."""
    return Article(
        title=row[1],
        link=row[2],
        summary=row[3],
        source_id=row[4],
        source_name=row[5],
        published=datetime.fromisoformat(row[6]) if row[6] else None,
        category=Category(row[7]),
        language=row[8],
        image_url=row[9],
        fetched_at=datetime.fromisoformat(row[10]),
    )


async def get_articles(
    db_path: str | None = None,
    category: str = "",
    language: str = "",
    source_id: str = "",
    limit: int = 50,
    offset: int = 0,
    today_only: bool = False,
) -> list[Article]:
    """Query stored articles with optional filters."""
    path = db_path or _db_path()
    conditions: list[str] = []
    params: list[str | int] = []

    if category:
        conditions.append("category = ?")
        params.append(category)
    if language:
        conditions.append("language = ?")
        params.append(language)
    if source_id:
        conditions.append("source_id = ?")
        params.append(source_id)
    if today_only:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conditions.append("fetched_at >= ?")
        params.append(today_str)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    query = f"SELECT * FROM articles {where} ORDER BY published DESC, fetched_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    async with aiosqlite.connect(path) as db:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [_row_to_article(row) for row in rows]


async def get_article_count(db_path: str | None = None, today_only: bool = False) -> int:
    """Get total count of articles in the database."""
    path = db_path or _db_path()
    query = "SELECT COUNT(*) FROM articles"
    params: list[str] = []
    if today_only:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        query += " WHERE fetched_at >= ?"
        params.append(today_str)

    async with aiosqlite.connect(path) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
