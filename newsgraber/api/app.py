"""FastAPI web application for NewsGraber."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

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


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    """Redirect to news page."""
    return RedirectResponse(url="/news")


@app.post("/api/fetch")
async def api_fetch(
    language: str = Query("", description="Filter by language code (en, zh, ja)"),
    category: str = Query("", description="Filter by category"),
):
    """Fetch latest news from all configured sources."""
    sources = list(DEFAULT_SOURCES)

    if category:
        try:
            cat = Category(category)
            sources = [s for s in sources if s.category == cat]
        except ValueError:
            return JSONResponse({"error": f"Unknown category: {category}"}, status_code=400)

    articles, results = await fetch_all(sources, language=language)

    if articles:
        await save_articles(articles)

    success = sum(1 for r in results if r.success)
    total_articles = sum(r.article_count for r in results if r.success)

    return {
        "success": success,
        "failed": len(results) - success,
        "total_articles": total_articles,
        "results": [r.model_dump() for r in results],
    }


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
    return {
        "total_articles": total,
        "today_articles": today,
        "sources_count": len(DEFAULT_SOURCES),
        "categories": [c.value for c in Category],
    }


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _qstr(cat: str = "", lang: str = "") -> str:
    """Build query string for filter links."""
    parts = []
    if cat:
        parts.append(f"category={cat}")
    if lang:
        parts.append(f"language={lang}")
    return "?" + "&".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# Apple-style CSS
# ---------------------------------------------------------------------------

_PAGE_CSS = """\
:root {
  --bg: #f5f5f7;
  --card-bg: #ffffff;
  --text: #1d1d1f;
  --text-secondary: #86868b;
  --accent: #0071e3;
  --accent-hover: #0077ed;
  --border: #d2d2d7;
  --tag-bg: #f0f0f3;
  --shadow: 0 2px 12px rgba(0,0,0,.08);
  --shadow-hover: 0 4px 20px rgba(0,0,0,.12);
  --radius: 16px;
  --radius-sm: 10px;
}
@media(prefers-color-scheme:dark){
  :root {
    --bg: #000; --card-bg: #1c1c1e; --text: #f5f5f7;
    --text-secondary: #98989d; --accent: #0a84ff; --accent-hover: #409cff;
    --border: #38383a; --tag-bg: #2c2c2e;
    --shadow: 0 2px 12px rgba(0,0,0,.3);
    --shadow-hover: 0 4px 20px rgba(0,0,0,.5);
  }
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text',
              'Helvetica Neue',Helvetica,Arial,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.5;
  -webkit-font-smoothing:antialiased;
}
.container{max-width:980px;margin:0 auto;padding:0 22px}

/* ── Header ── */
header{
  position:sticky;top:0;z-index:100;
  background:rgba(245,245,247,.72);
  backdrop-filter:saturate(180%) blur(20px);
  -webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:.5px solid var(--border);
}
@media(prefers-color-scheme:dark){
  header{background:rgba(0,0,0,.72)}
}
.header-inner{
  display:flex;align-items:center;justify-content:space-between;
  height:52px;gap:16px;
}
.logo{
  font-size:21px;font-weight:700;letter-spacing:-.02em;
  color:var(--text);text-decoration:none;white-space:nowrap;
}
.logo span{color:var(--accent)}
.header-actions{display:flex;align-items:center;gap:10px}

/* ── Buttons ── */
.btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 18px;font-size:14px;font-weight:500;
  border-radius:980px;border:none;cursor:pointer;
  transition:all .2s ease;text-decoration:none;white-space:nowrap;
}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:var(--accent-hover);transform:scale(1.02)}
.btn-primary:active{transform:scale(.98)}
.btn-primary:disabled{opacity:.5;cursor:not-allowed;transform:none}

/* ── Stats bar ── */
.stats-bar{
  display:flex;align-items:center;justify-content:center;
  gap:32px;padding:20px 0 8px;
}
.stat{text-align:center}
.stat-num{
  font-size:32px;font-weight:700;letter-spacing:-.03em;
  color:var(--text);line-height:1.1;
}
.stat-label{
  font-size:12px;font-weight:500;color:var(--text-secondary);
  text-transform:uppercase;letter-spacing:.04em;
}

/* ── Toast ── */
.toast{
  position:fixed;top:68px;left:50%;
  transform:translateX(-50%) translateY(-20px);
  padding:12px 24px;border-radius:var(--radius-sm);
  font-size:14px;font-weight:500;
  background:var(--card-bg);box-shadow:var(--shadow-hover);
  border:.5px solid var(--border);z-index:200;
  opacity:0;pointer-events:none;
  transition:all .35s cubic-bezier(.4,0,.2,1);
}
.toast.show{
  opacity:1;transform:translateX(-50%) translateY(0);pointer-events:auto;
}

/* ── Filters ── */
.filter-section{padding:12px 0 4px}
.filter-row{
  display:flex;align-items:center;gap:8px;
  padding:6px 0;flex-wrap:wrap;
}
.filter-label{
  font-size:12px;font-weight:600;color:var(--text-secondary);
  text-transform:uppercase;letter-spacing:.05em;
  min-width:52px;flex-shrink:0;
}
.chip{
  display:inline-flex;align-items:center;
  padding:6px 14px;font-size:13px;font-weight:500;
  border-radius:980px;background:var(--tag-bg);
  color:var(--text-secondary);text-decoration:none;
  transition:all .2s ease;white-space:nowrap;
  border:.5px solid transparent;
}
.chip:hover{background:var(--border);color:var(--text)}
.chip.active{background:var(--text);color:var(--bg);border-color:transparent}

/* ── Articles ── */
.articles{padding:8px 0 60px;display:flex;flex-direction:column;gap:10px}
.article-card{
  background:var(--card-bg);border-radius:var(--radius);
  padding:20px 24px;box-shadow:var(--shadow);
  transition:all .25s cubic-bezier(.4,0,.2,1);
  border:.5px solid var(--border);
}
.article-card:hover{box-shadow:var(--shadow-hover);transform:translateY(-1px)}
.article-title{
  font-size:17px;font-weight:600;letter-spacing:-.01em;
  line-height:1.35;margin-bottom:6px;
}
.article-title a{color:var(--text);text-decoration:none}
.article-title a:hover{color:var(--accent)}
.article-meta{
  display:flex;align-items:center;gap:8px;flex-wrap:wrap;
  margin-bottom:8px;font-size:13px;color:var(--text-secondary);
}
.article-source{font-weight:600;color:var(--accent)}
.article-tag{
  display:inline-flex;padding:2px 10px;font-size:11px;
  font-weight:600;text-transform:uppercase;letter-spacing:.03em;
  border-radius:980px;background:var(--tag-bg);color:var(--text-secondary);
}
.article-summary{
  font-size:15px;color:var(--text-secondary);line-height:1.55;
  display:-webkit-box;-webkit-line-clamp:3;
  -webkit-box-orient:vertical;overflow:hidden;
}

/* ── Empty state ── */
.empty-state{text-align:center;padding:80px 20px}
.empty-icon{font-size:56px;margin-bottom:16px;opacity:.6}
.empty-state h2{font-size:24px;font-weight:700;margin-bottom:8px}
.empty-state p{
  color:var(--text-secondary);font-size:15px;
  max-width:400px;margin:0 auto 24px;
}

/* ── Spinner ── */
.spinner{
  width:16px;height:16px;border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff;border-radius:50%;
  animation:spin .6s linear infinite;display:none;
}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Footer ── */
footer{
  text-align:center;padding:24px 0 40px;
  font-size:12px;color:var(--text-secondary);
}
footer a{color:var(--accent);text-decoration:none}

/* ── Responsive ── */
@media(max-width:600px){
  .stats-bar{gap:20px} .stat-num{font-size:24px}
  .article-card{padding:16px 18px} .header-inner{height:48px}
}
"""

# ---------------------------------------------------------------------------
# JavaScript
# ---------------------------------------------------------------------------

_PAGE_JS = """\
let fetchInProgress = false;

async function fetchNews(lang, cat) {
  if (fetchInProgress) return;
  fetchInProgress = true;

  const btn = document.getElementById('fetch-btn');
  const btnText = document.getElementById('fetch-text');
  const spinner = document.getElementById('fetch-spinner');

  btn.disabled = true;
  btnText.textContent = 'Fetching\u2026';
  spinner.style.display = 'block';

  try {
    let url = '/api/fetch?';
    if (lang) url += 'language=' + encodeURIComponent(lang) + '&';
    if (cat)  url += 'category=' + encodeURIComponent(cat) + '&';

    const res  = await fetch(url, { method: 'POST' });
    const data = await res.json();

    showToast('Fetched ' + data.total_articles + ' articles from ' + data.success + ' sources');
    setTimeout(() => { window.location.reload(); }, 1200);
  } catch (err) {
    showToast('Fetch failed: ' + err.message);
    btn.disabled = false;
    btnText.textContent = 'Fetch News';
    spinner.style.display = 'none';
    fetchInProgress = false;
  }
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => { toast.classList.remove('show'); }, 3500);
}
"""


# ---------------------------------------------------------------------------
# News HTML page
# ---------------------------------------------------------------------------

_CAT_LABELS = {
    "": "All",
    "general": "General",
    "world": "World",
    "politics": "Politics",
    "business": "Business",
    "technology": "Tech",
    "science": "Science",
    "health": "Health",
    "sports": "Sports",
    "entertainment": "Entertainment",
}

_LANG_LABELS = {"": "All", "en": "EN", "zh": "CN", "ja": "JP"}


@app.get("/news", response_class=HTMLResponse)
async def news_page(
    language: str = Query("", description="Filter by language"),
    category: str = Query("", description="Filter by category"),
):
    """Apple-style HTML news page with fetch button."""
    articles = await get_articles(
        language=language, category=category, limit=100, today_only=True,
    )
    if not articles:
        articles = await get_articles(language=language, category=category, limit=100)

    total = await get_article_count()
    today_count = await get_article_count(today_only=True)
    source_count = len(DEFAULT_SOURCES)

    # ── Build HTML ──
    parts: list[str] = []
    w = parts.append

    w("<!DOCTYPE html>")
    w('<html lang="en"><head>')
    w('<meta charset="UTF-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1.0">')
    w("<title>NewsGraber</title>")
    w(f"<style>{_PAGE_CSS}</style>")
    w("</head><body>")

    # Toast
    w('<div id="toast" class="toast"></div>')

    # Header
    w("<header><div class='container header-inner'>")
    w('  <a href="/news" class="logo">News<span>Graber</span></a>')
    w('  <div class="header-actions">')
    w(f'    <button class="btn btn-primary" id="fetch-btn"'
      f" onclick=\"fetchNews('{_esc(language)}','{_esc(category)}')\">")
    w('      <div class="spinner" id="fetch-spinner"></div>')
    w('      <span id="fetch-text">Fetch News</span>')
    w("    </button>")
    w("  </div>")
    w("</div></header>")

    w('<div class="container">')

    # Stats
    w('<div class="stats-bar">')
    for num, label in [(today_count, "Today"), (total, "Total"), (source_count, "Sources")]:
        w(f'<div class="stat"><div class="stat-num">{num}</div>'
          f'<div class="stat-label">{label}</div></div>')
    w("</div>")

    # Filters — two rows: category + language
    w('<div class="filter-section">')

    w('<div class="filter-row">')
    w('<span class="filter-label">Category</span>')
    for cat_val, label in _CAT_LABELS.items():
        active = " active" if cat_val == category else ""
        w(f'<a href="/news{_qstr(cat=cat_val, lang=language)}" class="chip{active}">{label}</a>')
    w("</div>")

    w('<div class="filter-row">')
    w('<span class="filter-label">Language</span>')
    for lang_val, label in _LANG_LABELS.items():
        active = " active" if lang_val == language else ""
        w(f'<a href="/news{_qstr(cat=category, lang=lang_val)}" class="chip{active}">{label}</a>')
    w("</div>")

    w("</div>")

    # Articles or empty
    if not articles:
        w('<div class="empty-state">')
        w('<div class="empty-icon">&#x1F4F0;</div>')
        w("<h2>No articles yet</h2>")
        w('<p>Click the "Fetch News" button above to grab the latest headlines from all sources.</p>')
        w("</div>")
    else:
        w('<div class="articles">')
        for a in articles:
            w('<div class="article-card">')
            w(f'<div class="article-title">'
              f'<a href="{_esc(a.link)}" target="_blank" rel="noopener">{_esc(a.title)}</a></div>')
            w(f'<div class="article-meta">'
              f'<span class="article-source">{_esc(a.source_name)}</span>'
              f"<span>&middot;</span><span>{a.display_time}</span>"
              f'<span class="article-tag">{a.category.value}</span></div>')
            if a.summary:
                w(f'<div class="article-summary">{_esc(a.summary)}</div>')
            w("</div>")
        w("</div>")

    # Footer
    w(f'<footer>NewsGraber v0.1.0 &middot; {source_count} sources &middot; '
      f'<a href="/docs">API Docs</a></footer>')

    w("</div>")
    w(f"<script>{_PAGE_JS}</script>")
    w("</body></html>")

    return HTMLResponse(content="\n".join(parts))
