"""CLI interface for NewsGraber using Click + Rich."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from newsgraber.config import get_settings
from newsgraber.fetcher import fetch_all
from newsgraber.models import Article, Category
from newsgraber.sources.registry import DEFAULT_SOURCES
from newsgraber.storage import get_article_count, get_articles, init_db, save_articles

console = Console()


def _run(coro):
    """Run an async coroutine from sync context."""
    return asyncio.run(coro)


@click.group()
@click.version_option(version="0.1.0", prog_name="newsgraber")
def main():
    """NewsGraber - Fetch today's headlines from major news sources worldwide."""
    pass


@main.command()
@click.option("--language", "-l", default="", help="Filter by language code (en, zh, ja)")
@click.option("--category", "-c", default="", help="Filter by category")
@click.option("--save/--no-save", default=True, help="Save fetched articles to database")
def fetch(language: str, category: str, save: bool):
    """Fetch latest news from all configured sources."""

    sources = DEFAULT_SOURCES
    if category:
        try:
            cat = Category(category)
            sources = [s for s in sources if s.category == cat]
        except ValueError:
            console.print(f"[red]Unknown category: {category}[/red]")
            console.print(f"Available: {', '.join(c.value for c in Category)}")
            raise SystemExit(1)

    console.print(
        Panel(
            f"[bold cyan]Fetching news from {len(sources)} source(s)...[/bold cyan]",
            title="NewsGraber",
        )
    )

    articles, results = _run(fetch_all(sources, language=language))

    # Show fetch results
    result_table = Table(title="Fetch Results", show_lines=False)
    result_table.add_column("Source", style="cyan", min_width=30)
    result_table.add_column("Status", justify="center", min_width=8)
    result_table.add_column("Articles", justify="right", min_width=8)

    success_count = 0
    for r in results:
        status = "[green]OK[/green]" if r.success else f"[red]FAIL[/red]"
        detail = str(r.article_count) if r.success else r.error[:40]
        result_table.add_row(r.source_name, status, detail)
        if r.success:
            success_count += 1

    console.print(result_table)
    console.print(
        f"\n[bold]{success_count}/{len(results)}[/bold] sources succeeded, "
        f"[bold green]{len(articles)}[/bold green] articles fetched."
    )

    if save and articles:
        _run(init_db())
        saved = _run(save_articles(articles))
        console.print(f"[dim]{saved} new articles saved to database.[/dim]")

    # Show top headlines
    if articles:
        _show_articles(articles[:15], title="Top Headlines")


@main.command(name="list")
@click.option("--language", "-l", default="", help="Filter by language code")
@click.option("--category", "-c", default="", help="Filter by category")
@click.option("--source", "-s", default="", help="Filter by source ID")
@click.option("--limit", "-n", default=20, help="Number of articles to show")
@click.option("--today", "-t", is_flag=True, help="Only show articles fetched today")
def list_articles(language: str, category: str, source: str, limit: int, today: bool):
    """List stored articles from the database."""
    _run(init_db())
    articles = _run(
        get_articles(
            category=category,
            language=language,
            source_id=source,
            limit=limit,
            today_only=today,
        )
    )

    if not articles:
        console.print("[yellow]No articles found. Run 'newsgraber fetch' first.[/yellow]")
        return

    _show_articles(articles, title="Stored Articles")


@main.command()
def sources():
    """List all configured news sources."""
    table = Table(title="Configured News Sources", show_lines=False)
    table.add_column("ID", style="dim", min_width=15)
    table.add_column("Name", style="cyan", min_width=30)
    table.add_column("Language", justify="center", min_width=8)
    table.add_column("Category", min_width=12)
    table.add_column("Country", justify="center", min_width=8)

    for s in DEFAULT_SOURCES:
        table.add_row(s.id, s.name, s.language, s.category.value, s.country)

    console.print(table)
    console.print(f"\n[bold]{len(DEFAULT_SOURCES)}[/bold] sources configured.")


@main.command()
def serve():
    """Start the web API server."""
    import uvicorn

    settings = get_settings()
    console.print(
        Panel(
            f"[bold green]Starting web server at http://{settings.host}:{settings.port}[/bold green]\n"
            f"API docs: http://localhost:{settings.port}/docs",
            title="NewsGraber Web",
        )
    )
    uvicorn.run(
        "newsgraber.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


@main.command()
def stats():
    """Show database statistics."""
    _run(init_db())
    total = _run(get_article_count())
    today = _run(get_article_count(today_only=True))

    console.print(Panel(
        f"Total articles: [bold]{total}[/bold]\n"
        f"Fetched today:  [bold green]{today}[/bold green]\n"
        f"Sources configured: [bold]{len(DEFAULT_SOURCES)}[/bold]",
        title="Database Stats",
    ))


def _show_articles(articles: list[Article], title: str = "News"):
    """Display articles in a formatted table."""
    table = Table(title=title, show_lines=True, padding=(0, 1))
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Time", style="dim", width=16)
    table.add_column("Source", style="cyan", width=20, no_wrap=True)
    table.add_column("Title", min_width=40)
    table.add_column("Category", style="magenta", width=12)

    for i, article in enumerate(articles, 1):
        table.add_row(
            str(i),
            article.display_time,
            article.source_name[:20],
            article.title,
            article.category.value,
        )

    console.print(table)


if __name__ == "__main__":
    main()
