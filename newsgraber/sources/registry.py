"""Registry of all supported news sources with their RSS feed URLs."""

from __future__ import annotations

from newsgraber.models import Category, NewsSource

DEFAULT_SOURCES: list[NewsSource] = [
    # === International / English ===
    NewsSource(
        id="bbc_top",
        name="BBC News - Top Stories",
        url="http://feeds.bbci.co.uk/news/rss.xml",
        language="en",
        category=Category.GENERAL,
        country="GB",
    ),
    NewsSource(
        id="bbc_world",
        name="BBC News - World",
        url="http://feeds.bbci.co.uk/news/world/rss.xml",
        language="en",
        category=Category.WORLD,
        country="GB",
    ),
    NewsSource(
        id="reuters_world",
        name="Reuters - World News",
        url="https://feeds.reuters.com/Reuters/worldNews",
        language="en",
        category=Category.WORLD,
        country="US",
    ),
    NewsSource(
        id="reuters_tech",
        name="Reuters - Technology",
        url="https://feeds.reuters.com/reuters/technologyNews",
        language="en",
        category=Category.TECHNOLOGY,
        country="US",
    ),
    NewsSource(
        id="ap_top",
        name="AP News - Top Stories",
        url="https://rsshub.app/apnews/topics/apf-topnews",
        language="en",
        category=Category.GENERAL,
        country="US",
    ),
    NewsSource(
        id="cnn_top",
        name="CNN - Top Stories",
        url="http://rss.cnn.com/rss/edition.rss",
        language="en",
        category=Category.GENERAL,
        country="US",
    ),
    NewsSource(
        id="cnn_world",
        name="CNN - World",
        url="http://rss.cnn.com/rss/edition_world.rss",
        language="en",
        category=Category.WORLD,
        country="US",
    ),
    NewsSource(
        id="nyt_home",
        name="New York Times - Home",
        url="https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        language="en",
        category=Category.GENERAL,
        country="US",
    ),
    NewsSource(
        id="nyt_world",
        name="New York Times - World",
        url="https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        language="en",
        category=Category.WORLD,
        country="US",
    ),
    NewsSource(
        id="guardian_world",
        name="The Guardian - World",
        url="https://www.theguardian.com/world/rss",
        language="en",
        category=Category.WORLD,
        country="GB",
    ),
    NewsSource(
        id="aljazeera",
        name="Al Jazeera",
        url="https://www.aljazeera.com/xml/rss/all.xml",
        language="en",
        category=Category.WORLD,
        country="QA",
    ),
    # === Technology ===
    NewsSource(
        id="techcrunch",
        name="TechCrunch",
        url="https://techcrunch.com/feed/",
        language="en",
        category=Category.TECHNOLOGY,
        country="US",
    ),
    NewsSource(
        id="ars_technica",
        name="Ars Technica",
        url="https://feeds.arstechnica.com/arstechnica/index",
        language="en",
        category=Category.TECHNOLOGY,
        country="US",
    ),
    NewsSource(
        id="hacker_news",
        name="Hacker News - Best",
        url="https://hnrss.org/best",
        language="en",
        category=Category.TECHNOLOGY,
        country="US",
    ),
    # === Science ===
    NewsSource(
        id="nature",
        name="Nature - Latest Research",
        url="https://www.nature.com/nature.rss",
        language="en",
        category=Category.SCIENCE,
        country="GB",
    ),
    # === Business ===
    NewsSource(
        id="bloomberg",
        name="Bloomberg",
        url="https://feeds.bloomberg.com/markets/news.rss",
        language="en",
        category=Category.BUSINESS,
        country="US",
    ),
    # === 中文 / Chinese ===
    NewsSource(
        id="xinhua",
        name="新华网 - 时政",
        url="http://www.xinhuanet.com/politics/news_politics.xml",
        language="zh",
        category=Category.POLITICS,
        country="CN",
    ),
    NewsSource(
        id="zaobao",
        name="联合早报 - 即时",
        url="https://rsshub.app/zaobao/realtime/china",
        language="zh",
        category=Category.GENERAL,
        country="SG",
    ),
    # === 日本語 / Japanese ===
    NewsSource(
        id="nhk",
        name="NHK News",
        url="https://www.nhk.or.jp/rss/news/cat0.xml",
        language="ja",
        category=Category.GENERAL,
        country="JP",
    ),
]


def get_sources_by_category(category: Category) -> list[NewsSource]:
    return [s for s in DEFAULT_SOURCES if s.category == category]


def get_sources_by_language(language: str) -> list[NewsSource]:
    return [s for s in DEFAULT_SOURCES if s.language == language]
