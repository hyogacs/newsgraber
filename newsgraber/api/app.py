"""FastAPI web application for NewsGraber."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from newsgraber.fetcher import fetch_all
from newsgraber.models import Article, Category, FetchResult
from newsgraber.sources.registry import DEFAULT_SOURCES
from newsgraber.storage import get_article_count, get_articles, init_db, save_articles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="NewsGraber API",
    description="News aggregator that fetches today's headlines from major news sources worldwide.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Landing page with quick overview."""
    total = await get_article_count()
    today = await get_article_count(today_only=True)
    return {
        "name": "NewsGraber",
        "version": "0.1.0",
        "total_articles": total,
        "today_articles": today,
        "sources_count": len(DEFAULT_SOURCES),
        "endpoints": {
            "articles": "/api/articles",
            "fetch": "/api/fetch",
            "sources": "/api/sources",
            "stats": "/api/stats",
            "docs": "/docs",
        },
    }


@app.post("/api/fetch", response_model=list[FetchResult])
async def api_fetch(
    language: str = Query("", description="Filter by language code (en, zh, ja)"),
    category: str = Query("", description="Filter by category"),
    save: bool = Query(True, description="Save to database"),
):
    """Fetch latest news from all configured sources."""
    sources = DEFAULT_SOURCES

    if category:
        try:
            cat = Category(category)
            sources = [s for s in sources if s.category == cat]
        except ValueError:
            return {"error": f"Unknown category: {category}"}

    articles, results = await fetch_all(sources, language=language)

    if save and articles:
        await save_articles(articles)

    return results


@app.get("/api/articles", response_model=list[Article])
async def api_articles(
    category: str = Query("", description="Filter by category"),
    language: str = Query("", description="Filter by language code"),
    source: str = Query("", description="Filter by source ID"),
    limit: int = Query(50, ge=1, le=200, description="Max articles to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    today: bool = Query(False, description="Only articles fetched today"),
):
    """Get stored articles with optional filters."""
    return await get_articles(
        category=category,
        language=language,
        source_id=source,
        limit=limit,
        offset=offset,
        today_only=today,
    )


@app.get("/api/sources")
async def api_sources():
    """List all configured news sources."""
    return [s.model_dump() for s in DEFAULT_SOURCES]


@app.get("/api/stats")
async def api_stats():
    """Get database statistics."""
    total = await get_article_count()
    today = await get_article_count(today_only=True)
    categories = {}
    for cat in Category:
        cat_articles = await get_articles(category=cat.value, limit=1)
        categories[cat.value] = len(cat_articles) > 0

    return {
        "total_articles": total,
        "today_articles": today,
        "sources_count": len(DEFAULT_SOURCES),
        "categories": [c.value for c in Category],
    }


@app.get("/news", response_class=HTMLResponse)
async def news_page(
    language: str = Query("", description="Filter by language"),
    category: str = Query("", description="Filter by category"),
):
    """Simple HTML page showing latest news."""
    articles = await get_articles(
        language=language,
        category=category,
        limit=100,
        today_only=True,
    )
    if not articles:
        articles = await get_articles(language=language, category=category, limit=100)

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "<title>NewsGraber - Today's Headlines</title>",
        "<style>",
        "  * { margin: 0; padding: 0; box-sizing: border-box; }",
        "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
        "         background: #0f172a; color: #e2e8f0; line-height: 1.6; }",
        "  .container { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }",
        "  h1 { text-align: center; margin-bottom: 0.5rem; color: #38bdf8; font-size: 2rem; }",
        "  .subtitle { text-align: center; color: #94a3b8; margin-bottom: 2rem; }",
        "  .filters { text-align: center; margin-bottom: 2rem; }",
        "  .filters a { color: #38bdf8; text-decoration: none; margin: 0 0.5rem;",
        "               padding: 0.25rem 0.75rem; border: 1px solid #334155; border-radius: 1rem; }",
        "  .filters a:hover, .filters a.active { background: #1e293b; }",
        "  .article { background: #1e293b; border-radius: 0.5rem; padding: 1.25rem;",
        "             margin-bottom: 1rem; border-left: 3px solid #38bdf8; }",
        "  .article:hover { border-left-color: #f472b6; }",
        "  .article h2 { font-size: 1.1rem; margin-bottom: 0.5rem; }",
        "  .article h2 a { color: #f1f5f9; text-decoration: none; }",
        "  .article h2 a:hover { color: #38bdf8; }",
        "  .meta { font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.5rem; }",
        "  .meta .source { color: #38bdf8; }",
        "  .meta .category { color: #f472b6; background: #1e1b3a; padding: 0.1rem 0.5rem;",
        "                    border-radius: 0.75rem; font-size: 0.75rem; }",
        "  .summary { color: #cbd5e1; font-size: 0.95rem; }",
        "  .empty { text-align: center; padding: 3rem; color: #64748b; }",
        "  footer { text-align: center; color: #475569; margin-top: 3rem; font-size: 0.85rem; }",
        "</style></head><body>",
        '<div class="container">',
        "<h1>NewsGraber</h1>",
        f'<p class="subtitle">{len(articles)} articles</p>',
        '<div class="filters">',
        '  <a href="/news">All</a>',
    ]

    for cat in Category:
        html_parts.append(f'  <a href="/news?category={cat.value}">{cat.value.title()}</a>')

    html_parts.append("</div>")

    if not articles:
        html_parts.append(
            '<div class="empty">No articles yet. '
            'Use <code>POST /api/fetch</code> or run <code>newsgraber fetch</code> first.</div>'
        )
    else:
        for a in articles:
            html_parts.extend([
                '<div class="article">',
                f'  <h2><a href="{a.link}" target="_blank" rel="noopener">{a.title}</a></h2>',
                f'  <div class="meta">',
                f'    <span class="source">{a.source_name}</span> &middot; {a.display_time}',
                f'    &middot; <span class="category">{a.category.value}</span>',
                f"  </div>",
            ])
            if a.summary:
                html_parts.append(f'  <div class="summary">{a.summary}</div>')
            html_parts.append("</div>")

    html_parts.extend([
        '<footer>NewsGraber v0.1.0 &middot; Powered by RSS</footer>',
        "</div></body></html>",
    ])

    return "\n".join(html_parts)
