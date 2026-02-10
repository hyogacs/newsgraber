# CLAUDE.md — newsgraber

> This file provides context for AI assistants (Claude, Copilot, etc.) working on the **newsgraber** project. Update it as the project evolves.

## Project Overview

**newsgraber** is a news aggregation/scraping project. The repository is currently in its initial bootstrapping phase with no application code yet committed.

- **Repository**: `hyogacs/newsgraber`
- **Status**: Bootstrapping — no source code, build system, or dependencies have been added yet.

## Repository Structure

```
newsgraber/
├── CLAUDE.md          # This file — AI assistant guide
└── .git/              # Git metadata
```

> Update this tree as directories and files are added.

## Development Guidelines

### Git Workflow

- **Default branch**: `main` (to be established with the first commit)
- Create feature branches from the default branch.
- Write clear, descriptive commit messages summarizing the *why*, not just the *what*.
- Do not force-push to shared branches.

### Code Conventions (to be established)

As the project takes shape, document the following here:

- Programming language(s) and version(s)
- Package manager and dependency installation commands
- Linting / formatting tools and commands
- Naming conventions (files, variables, functions, classes)
- Project architecture patterns (MVC, modular, monorepo, etc.)

### Build & Run (to be established)

```bash
# Install dependencies
# <add command here>

# Run the application
# <add command here>

# Run tests
# <add command here>

# Lint / format
# <add command here>
```

### Testing (to be established)

- Test framework: TBD
- Test location: TBD
- Coverage requirements: TBD

### Environment & Configuration (to be established)

- Required environment variables: TBD
- Configuration files: TBD
- Secrets management: TBD

## Instructions for AI Assistants

1. **Read before writing.** Always read existing files before proposing changes.
2. **Keep it simple.** Only make changes that are directly requested or clearly necessary. Avoid over-engineering.
3. **No guessing.** If the project structure or conventions are unclear, explore the codebase first.
4. **Security first.** Never commit secrets, credentials, or `.env` files. Validate user input at system boundaries.
5. **Update this file.** When you add significant infrastructure (build system, test framework, CI/CD, new directories), update the relevant sections of this CLAUDE.md so future sessions have accurate context.
6. **Commit hygiene.** Stage specific files rather than using `git add .` to avoid accidentally committing unwanted files.
