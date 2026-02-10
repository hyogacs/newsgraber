"""Tests for data models."""

from datetime import datetime, timezone

from newsgraber.models import Article, Category, FetchResult, NewsSource


def test_news_source_defaults():
    source = NewsSource(id="test", name="Test Source", url="http://example.com/rss")
    assert source.language == "en"
    assert source.category == Category.GENERAL
    assert source.country == ""


def test_article_display_time_with_published():
    article = Article(
        title="Test",
        link="http://example.com/1",
        source_id="test",
        source_name="Test",
        published=datetime(2025, 1, 15, 10, 30, tzinfo=timezone.utc),
    )
    assert article.display_time == "2025-01-15 10:30"


def test_article_display_time_without_published():
    article = Article(
        title="Test",
        link="http://example.com/1",
        source_id="test",
        source_name="Test",
    )
    # Should fall back to fetched_at
    assert article.display_time is not None
    assert len(article.display_time) == 16  # YYYY-MM-DD HH:MM


def test_fetch_result():
    result = FetchResult(
        source_id="test",
        source_name="Test",
        success=True,
        article_count=5,
    )
    assert result.success
    assert result.article_count == 5
    assert result.error == ""


def test_category_values():
    assert Category.WORLD.value == "world"
    assert Category.TECHNOLOGY.value == "technology"
