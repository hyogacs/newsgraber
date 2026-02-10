"""Tests for the SQLite storage layer."""

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from newsgraber.models import Article, Category
from newsgraber.storage import get_article_count, get_articles, init_db, save_articles


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def sample_articles():
    return [
        Article(
            title="Article One",
            link="http://example.com/1",
            summary="First article",
            source_id="test",
            source_name="Test Source",
            published=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc),
            category=Category.TECHNOLOGY,
            language="en",
        ),
        Article(
            title="Article Two",
            link="http://example.com/2",
            summary="Second article",
            source_id="test",
            source_name="Test Source",
            published=datetime(2025, 6, 1, 11, 0, tzinfo=timezone.utc),
            category=Category.WORLD,
            language="en",
        ),
        Article(
            title="文章三",
            link="http://example.com/3",
            summary="第三篇文章",
            source_id="xinhua",
            source_name="新华网",
            published=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
            category=Category.POLITICS,
            language="zh",
        ),
    ]


@pytest.mark.asyncio
async def test_init_db(db_path):
    await init_db(db_path)
    assert Path(db_path).exists()


@pytest.mark.asyncio
async def test_save_and_retrieve(db_path, sample_articles):
    await init_db(db_path)
    saved = await save_articles(sample_articles, db_path)
    assert saved > 0

    articles = await get_articles(db_path=db_path)
    assert len(articles) == 3


@pytest.mark.asyncio
async def test_duplicate_links_ignored(db_path, sample_articles):
    await init_db(db_path)
    await save_articles(sample_articles, db_path)
    # Save again - duplicates should be ignored
    await save_articles(sample_articles, db_path)

    count = await get_article_count(db_path=db_path)
    assert count == 3


@pytest.mark.asyncio
async def test_filter_by_category(db_path, sample_articles):
    await init_db(db_path)
    await save_articles(sample_articles, db_path)

    tech = await get_articles(db_path=db_path, category="technology")
    assert len(tech) == 1
    assert tech[0].title == "Article One"


@pytest.mark.asyncio
async def test_filter_by_language(db_path, sample_articles):
    await init_db(db_path)
    await save_articles(sample_articles, db_path)

    zh = await get_articles(db_path=db_path, language="zh")
    assert len(zh) == 1
    assert zh[0].title == "文章三"


@pytest.mark.asyncio
async def test_filter_by_source(db_path, sample_articles):
    await init_db(db_path)
    await save_articles(sample_articles, db_path)

    xinhua = await get_articles(db_path=db_path, source_id="xinhua")
    assert len(xinhua) == 1


@pytest.mark.asyncio
async def test_pagination(db_path, sample_articles):
    await init_db(db_path)
    await save_articles(sample_articles, db_path)

    page1 = await get_articles(db_path=db_path, limit=2, offset=0)
    assert len(page1) == 2

    page2 = await get_articles(db_path=db_path, limit=2, offset=2)
    assert len(page2) == 1
