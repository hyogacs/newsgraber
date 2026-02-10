"""Tests for source registry."""

from newsgraber.models import Category
from newsgraber.sources.registry import DEFAULT_SOURCES, get_sources_by_category, get_sources_by_language


def test_default_sources_not_empty():
    assert len(DEFAULT_SOURCES) > 0


def test_all_sources_have_required_fields():
    for source in DEFAULT_SOURCES:
        assert source.id, f"Source missing id: {source}"
        assert source.name, f"Source missing name: {source}"
        assert source.url, f"Source missing url: {source}"
        assert source.language, f"Source missing language: {source}"


def test_source_ids_unique():
    ids = [s.id for s in DEFAULT_SOURCES]
    assert len(ids) == len(set(ids)), "Duplicate source IDs found"


def test_get_sources_by_category():
    tech = get_sources_by_category(Category.TECHNOLOGY)
    assert len(tech) >= 1
    assert all(s.category == Category.TECHNOLOGY for s in tech)


def test_get_sources_by_language():
    en = get_sources_by_language("en")
    assert len(en) >= 1
    assert all(s.language == "en" for s in en)

    zh = get_sources_by_language("zh")
    assert len(zh) >= 1
    assert all(s.language == "zh" for s in zh)
