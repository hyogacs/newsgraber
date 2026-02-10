"""Tests for the news fetcher engine."""

from newsgraber.fetcher import _clean_html, _parse_feed
from newsgraber.models import Category, NewsSource


def test_clean_html_strips_tags():
    assert _clean_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_clean_html_decodes_entities():
    assert _clean_html("&amp; &lt; &gt;") == "& < >"


def test_clean_html_empty():
    assert _clean_html("") == ""
    assert _clean_html(None) == ""


def test_parse_feed_valid_rss():
    source = NewsSource(id="test", name="Test", url="http://example.com/rss")
    rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Test Feed</title>
        <item>
          <title>Article One</title>
          <link>http://example.com/1</link>
          <description>Summary of article one</description>
          <pubDate>Mon, 01 Jan 2025 12:00:00 GMT</pubDate>
        </item>
        <item>
          <title>Article Two</title>
          <link>http://example.com/2</link>
          <description>Summary of article two</description>
        </item>
      </channel>
    </rss>"""
    articles = _parse_feed(rss, source, max_items=10)
    assert len(articles) == 2
    assert articles[0].title == "Article One"
    assert articles[0].link == "http://example.com/1"
    assert articles[0].summary == "Summary of article one"
    assert articles[0].source_id == "test"
    assert articles[1].title == "Article Two"


def test_parse_feed_respects_max_items():
    source = NewsSource(id="test", name="Test", url="http://example.com/rss")
    rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Test</title>
        <item><title>One</title><link>http://1</link></item>
        <item><title>Two</title><link>http://2</link></item>
        <item><title>Three</title><link>http://3</link></item>
      </channel>
    </rss>"""
    articles = _parse_feed(rss, source, max_items=2)
    assert len(articles) == 2


def test_parse_feed_empty():
    source = NewsSource(id="test", name="Test", url="http://example.com/rss")
    articles = _parse_feed("", source, max_items=10)
    assert articles == []


def test_parse_feed_skips_untitled():
    source = NewsSource(id="test", name="Test", url="http://example.com/rss")
    rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item><title></title><link>http://1</link></item>
        <item><title>Valid</title><link>http://2</link></item>
      </channel>
    </rss>"""
    articles = _parse_feed(rss, source, max_items=10)
    assert len(articles) == 1
    assert articles[0].title == "Valid"
