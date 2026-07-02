# RepoMind AI — Documentation Index

> **Purpose of this folder:** Detailed, up-to-date reference for LLMs, coding agents, and developers working on this project. Read this file first, then follow the links below based on your task.

## Project in One Paragraph

**RepoMind AI** (also called **OpenSeek**) is a CS313 Information Retrieval project that scrapes GitHub repositories, processes them with NLP, indexes them with a hybrid **BM25 + sentence-transformer** search engine, and serves them through a **FastAPI backend** and **React frontend**. Users complete a profile wizard for cold-start recommendations, run personalized hybrid search, explore similar repos, get rule-based project explanations, and optionally use **local Ollama LLM** features for grounded repo explanations and roadmaps.

---

## Quick Start (for agents that need to run the app)

```bash
# From project root — processed.json must exist
# Start PostgreSQL first: docker compose up -d
# Run migrations: alembic upgrade head && python -m backend.database.seed_roles
uvicorn backend.main:app --reload --port 8000

# Separate terminal
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

Optional for AI features: run Ollama locally (`ollama serve`, pull `qwen2.5:1.5b` or set `OLLAMA_MODEL`).

---

## Documentation Map

| Document | When to read it |
|---|---|
| [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) | High-level purpose, features, tech stack, module map |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System layers, diagrams, data flows, design decisions |
| [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md) | Every folder and file, what it does |
| [FILE_REFERENCE.md](./FILE_REFERENCE.md) | Per-file classification (core / supporting / deprecated) |
| [API_REFERENCE.md](./API_REFERENCE.md) | All REST endpoints with request/response shapes |
| [AI_PIPELINE.md](./AI_PIPELINE.md) | Search scoring, rule-based AI, and Ollama RAG pipeline |
| [EXECUTION_PIPELINE.md](./EXECUTION_PIPELINE.md) | Offline data pipeline + online request flows |
| [RUN_ORDER.md](./RUN_ORDER.md) | Step-by-step setup guide for humans |
| [CONFIGURATION.md](./CONFIGURATION.md) | Env vars, ports, model settings, scoring weights |
| [DEPENDENCY_GRAPH.md](./DEPENDENCY_GRAPH.md) | Import relationships between modules |
| [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) | Gotchas, inconsistencies, and workarounds |
| [DATABASE.md](./DATABASE.md) | PostgreSQL, SQLAlchemy models, Alembic migrations |
| [AUTHENTICATION.md](./AUTHENTICATION.md) | JWT auth, refresh tokens, security |
| [USER_MANAGEMENT.md](./USER_MANAGEMENT.md) | Profiles, preferences, favorites, history |

---

## Current Architecture (July 2026)

```
Data pipeline (offline)
  scraper.py → new_data.json → process.py → processed.json

Search index (lazy, on first API request)
  semantic_hybrid_recommender.py → vector_db/{bm25_index.json, repo_embeddings.npy, repo_metadata.json}

Backend (FastAPI :8000) — 12 routers
  /search, /recommend, /repos, /profile
  /api/advisor, /api/project-explainer, /api/rag
  /auth, /users, /users/preferences, /users/favorites, /users/history

Frontend (React + Vite :5173)
  Profile wizard → profile recommendations → hybrid search → repo cards
  Repo cards: Explain Project (rule-based), Explain with AI (Ollama), AI Roadmap (Ollama)
```

---

## Critical Facts for Agents

1. **Run uvicorn from project root** — root-level imports (`repo_utils`, `semantic_hybrid_recommender`, `smart_profile_recommender_v2`) require CWD = project root.
2. **Search engine lives in `semantic_hybrid_recommender.py`** — there is no `core/search_engine.py` anymore.
3. **Index directory is `vector_db/`** — not `storage/`.
4. **Two AI systems coexist:**
   - **Rule-based** (`backend/core/repo_explainer.py`, `project_explainer.py`, `ai_advisor.py`) — no external API, instant.
   - **Ollama RAG** (`backend/core/rag_advisor.py`, `llm_client.py`) — requires local Ollama server.
5. **Advisor UI components exist but are not mounted in `App.jsx`** — the API works; `AdvisorButtons`, `AdvisorSummaryPanel`, etc. are available for integration.
6. **RAG frontend uses `VITE_API_BASE_URL`**; main client uses `VITE_API_URL` — see [KNOWN_ISSUES.md](./KNOWN_ISSUES.md).
7. **`processed.json` is ~58 MB** — primary dataset; must exist before search works.
8. **Postgres is wired** — user management via SQLAlchemy; see [DATABASE.md](./DATABASE.md).

---

## Related Root-Level Docs (not in /docs)

| File | Notes |
|---|---|
| `README.md` | User-facing overview (partially outdated) |
| `PROJECT_A_TO_Z.md` | Extended project guide |
| `EXCUTION.md`, `Pipeline.md` | Older execution/pipeline notes |
| `COURSE-REQUIREMENTS.md` | Academic requirements checklist |
| `SCRAPER_DOCUMENTATION.md` | Scraper-specific docs |

Prefer **`/docs`** for agent context — it reflects the current codebase.
