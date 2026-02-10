# CLAUDE.md — newsgraber

> This file provides context for AI assistants (Claude, Copilot, etc.) working on the **newsgraber** project. Update it as the project evolves.

## Project Overview

**newsgraber** is a Python news aggregation app that fetches today's headlines from major news sources worldwide via RSS feeds. It provides both a CLI and a web API (FastAPI) for fetching, browsing, and filtering news.

- **Repository**: `hyogacs/newsgraber`
- **Status**: v0.1.0 — core functionality implemented

## Repository Structure

```
newsgraber/
├── CLAUDE.md              # AI assistant guide
├── pyproject.toml         # Project metadata, dependencies, tool config
├── requirements.txt       # Pip requirements
├── .env.example           # Environment variable reference
├── .gitignore
├── newsgraber/            # Main package
│   ├── __init__.py
│   ├── models.py          # Pydantic data models (Article, NewsSource, etc.)
│   ├── config.py          # Settings via pydantic-settings + .env
│   ├── fetcher.py         # Async RSS fetch engine (httpx + feedparser)
│   ├── storage.py         # SQLite persistence layer (aiosqlite)
│   ├── cli.py             # CLI interface (click + rich)
│   ├── sources/
│   │   ├── __init__.py
│   │   └── registry.py    # RSS source definitions (BBC, CNN, NYT, etc.)
│   └── api/
│       ├── __init__.py
│       └── app.py         # FastAPI web application
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_fetcher.py
    ├── test_storage.py
    └── test_sources.py
```

## Development Guidelines

### Git Workflow

- **Default branch**: `main`
- Create feature branches from the default branch.
- Write clear, descriptive commit messages summarizing the *why*, not just the *what*.
- Do not force-push to shared branches.

### Code Conventions

- **Language**: Python 3.10+
- **Package manager**: pip (requirements.txt / pyproject.toml)
- **Linting / formatting**: ruff (`ruff check .`, `ruff format .`)
- **Type hints**: Used throughout via `from __future__ import annotations`
- **Naming**: snake_case for files/functions/variables, PascalCase for classes
- **Architecture**: Modular — models, fetcher engine, storage, CLI, API are separate layers

### Build & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch latest news (CLI)
python -m newsgraber.cli fetch

# Fetch only English news
python -m newsgraber.cli fetch -l en

# Fetch only technology news
python -m newsgraber.cli fetch -c technology

# List stored articles
python -m newsgraber.cli list

# Show configured sources
python -m newsgraber.cli sources

# Start web API server
python -m newsgraber.cli serve

# Run tests
python -m pytest tests/ -v

# Lint
ruff check .
```

### Testing

- **Test framework**: pytest + pytest-asyncio
- **Test location**: `tests/`
- **Run**: `python -m pytest tests/ -v`

### Environment & Configuration

- All settings via env vars prefixed with `NEWSGRABER_` (see `.env.example`)
- Copy `.env.example` to `.env` and modify as needed
- Key settings: `NEWSGRABER_DB_PATH`, `NEWSGRABER_FETCH_TIMEOUT`, `NEWSGRABER_PORT`
- No secrets required — all news sources use public RSS feeds

## Instructions for AI Assistants

1. **Read before writing.** Always read existing files before proposing changes.
2. **Keep it simple.** Only make changes that are directly requested or clearly necessary. Avoid over-engineering.
3. **No guessing.** If the project structure or conventions are unclear, explore the codebase first.
4. **Security first.** Never commit secrets, credentials, or `.env` files. Validate user input at system boundaries.
5. **Update this file.** When you add significant infrastructure (build system, test framework, CI/CD, new directories), update the relevant sections of this CLAUDE.md so future sessions have accurate context.
6. **Commit hygiene.** Stage specific files rather than using `git add .` to avoid accidentally committing unwanted files.
