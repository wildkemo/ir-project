# Database Layer — RepoMind AI

## Overview

RepoMind AI uses **PostgreSQL** for user management, authentication, preferences, favorites, and activity history. Repository metadata remains in `processed.json`, BM25, and Qdrant — the database stores **references only** (e.g. `microsoft/vscode`).

## Technology

| Component | Package |
|---|---|
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Driver | psycopg2 |
| Primary keys | UUID |

## Directory Structure

```
backend/database/
├── __init__.py
├── config.py          # Connection URL from env
├── session.py         # Engine + SessionLocal + get_db()
├── base.py            # Declarative Base
├── seed_roles.py      # Seed User + Admin roles
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/      # Alembic revisions
```

## Models

| Model | Table | Purpose |
|---|---|---|
| `Role` | `roles` | User / Admin RBAC |
| `User` | `users` | Account identity |
| `RefreshToken` | `refresh_tokens` | JWT refresh rotation |
| `UserPreference` | `user_preferences` | Experience, license, profile fields |
| `PreferredLanguage` | `preferred_languages` | Language list |
| `PreferredTopic` | `preferred_topics` | Topic list |
| `PreferredFramework` | `preferred_frameworks` | Framework list |
| `FavoriteRepository` | `favorite_repositories` | `owner/repo` references |
| `SearchHistory` | `search_history` | Query + type + result count |
| `RecommendationHistory` | `recommendation_history` | Repo + score + reason |
| `AIRequest` | `ai_requests` | AI feature usage tracking |

## Setup

```bash
# Start PostgreSQL (docker-compose)
docker compose up -d

# Configure .env (see .env.example)
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed default roles
python -m backend.database.seed_roles
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | _(built from parts)_ | Full SQLAlchemy URL |
| `POSTGRES_USER` | `repomind` | DB user |
| `POSTGRES_PASSWORD` | `repomind123` | DB password |
| `POSTGRES_HOST` | `127.0.0.1` | DB host |
| `POSTGRES_PORT` | `5433` | Host port (docker maps 5433→5432) |
| `POSTGRES_DB` | `repomind` | Database name |

## Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## Design Rules

- **No raw SQL** in application code — SQLAlchemy ORM only
- **No repository metadata** in PostgreSQL
- Alembic `env.py` imports `backend.models` so all tables are detected
- Search/recommendation engines unchanged — DB layer is additive
