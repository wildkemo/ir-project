# RepoMind AI — Project Overview

## Purpose

**RepoMind AI** (internally called **OpenSeek**) is a **Web Intelligence Data Pipeline and Personalized GitHub Repository Discovery Engine** built for **CS313x – Information Retrieval & Data Analysis**.

The project:

1. **Collects** open-source GitHub repository data (scraper + GitHub API)
2. **Processes** it with NLP (tokenization, stemming, lemmatization, scoring)
3. **Indexes** it for hybrid BM25 + semantic search
4. **Serves** it through a FastAPI + React web application

Users can search, get profile-based recommendations, understand repositories, compare repos, generate roadmaps, and optionally use a **local Ollama LLM** for grounded explanations.

---

## Main Features

| Feature | Type | Description |
|---|---|---|
| Hybrid Search | IR | BM25 (lexical) + Sentence-Transformer (semantic) + popularity scoring |
| Profile Recommendation | IR | Multi-dimensional profile questionnaire + weighted scoring |
| Personalized Search | IR | Query + profile enrichment and re-ranking |
| Similar Repos | IR | Embedding cosine similarity from a seed repository |
| Score Breakdown | UI | BM25, semantic, and profile/popularity components per result |
| Project Explainer | Rule-based AI | Deep README analysis, sections, metrics, strengths/limitations |
| AI Advisor API | Rule-based AI | Explain, roadmap, compare, multi-repo summary |
| RAG Explain / Roadmap | Ollama LLM | Grounded natural-language explanations using repo context |
| Profile Wizard | UI | 6-step questionnaire with localStorage persistence |
| Query-Only Mode | UI | Toggle to disable profile bias in search ranking |

---

## Technology Stack

### Backend

| Component | Technology |
|---|---|
| Web Framework | FastAPI 0.136+ |
| ASGI Server | Uvicorn |
| Data Validation | Pydantic v2 |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| BM25 Engine | Pure-Python implementation in `semantic_hybrid_recommender.py` |
| Vector Storage | NumPy `.npy` + JSON in `vector_db/` |
| NLP Preprocessing | NLTK (stopwords, WordNet lemmatization) |
| Local LLM | Ollama HTTP API (`qwen2.5:1.5b` default) |
| HTTP | Requests + BeautifulSoup4 (scraper) |

### Frontend

| Component | Technology |
|---|---|
| Framework | React 19 |
| Build Tool | Vite 8 |
| HTTP Client | Axios (`client.js`, `advisor.js`) + fetch (`ragAdvisor.js`) |
| Icons | Lucide React |
| Styling | Vanilla CSS with dark/light theme |
| Dev Proxy | Vite proxy `/api` → `http://127.0.0.1:8000` |

### Optional / Infrastructure

| Component | Technology | Status |
|---|---|---|
| Vector DB | Qdrant via `quadrant_updater.py` | Optional, not used by main backend |
| Database | PostgreSQL 17 in `docker-compose.yml` | **Wired** — user management via SQLAlchemy |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE (offline)                  │
│  scraper.py → new_data.json → process.py → processed.json   │
│                     analysis.py (stats report)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              SEARCH INDEX (lazy, first API request)            │
│  semantic_hybrid_recommender.py (GitHubRepoSearchEngine)     │
│  → vector_db/bm25_index.json + repo_embeddings.npy           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI :8000)                    │
│  backend/main.py — 7 routers:                                │
│  ├── /search, /recommend, /repos, /profile                   │
│  ├── /api/advisor        (rule-based AI)                     │
│  ├── /api/project-explainer                                  │
│  └── /api/rag            (Ollama LLM)                        │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                FRONTEND (React + Vite :5173)                 │
│  Profile Wizard → Recommendations → Search → Repo Cards      │
│  Actions: Explain Project | Explain with AI | AI Roadmap     │
│  Similar repos side panel                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Main Modules

| Module | Location | Role |
|---|---|---|
| Data Scraper | `scraper.py` | GitHub topic crawling + API repo extraction |
| Data Processor | `process.py` | NLP tokenization, normalization, scoring |
| Data Analyzer | `analysis.py` | Dataset statistics |
| Search Engine | `semantic_hybrid_recommender.py` | `GitHubRepoSearchEngine`, `BM25Index`, CLI |
| Profile Recommender | `smart_profile_recommender_v2.py` | Profile matching + personalized search |
| Repo Utils | `repo_utils.py` | GitHub URL validation, doc filtering |
| Semantic Loader | `backend/core/semantic_loader.py` | Singleton engine + search adapters |
| Profile Loader | `backend/core/profile_loader.py` | Profile recommender adapter |
| Repo Intelligence | `backend/core/repo_intelligence.py` | Tech stack, README sections, health scores |
| Repo Explainer | `backend/core/repo_explainer.py` | Rule-based per-repo explanation |
| Project Explainer | `backend/core/project_explainer.py` | Deep README structured analysis |
| Roadmap Generator | `backend/core/roadmap_generator.py` | Goal-aware step lists |
| Repo Comparator | `backend/core/repo_comparator.py` | Side-by-side comparison |
| AI Advisor | `backend/core/ai_advisor.py` | Multi-repo advisory summary |
| RAG Advisor | `backend/core/rag_advisor.py` | Ollama-grounded explain + roadmap |
| LLM Client | `backend/core/llm_client.py` | Ollama HTTP chat client |

---

## User-Facing Flow

1. **First visit:** Profile wizard asks about project type, language, goal, level, repo kind, complexity.
2. **Profile results:** Up to 10 repos ranked by profile match (shown before any search).
3. **Search:** User queries the hybrid engine; optional profile enrichment unless "Query Only Mode" is on.
4. **Per-repo actions** (search result cards):
   - **Why this result?** — score decomposition (`POST /search/explain`)
   - **Explain Project** — rule-based deep analysis (`POST /api/project-explainer/explain`)
   - **Explain with AI** — Ollama RAG (`POST /api/rag/explain`)
   - **AI Roadmap** — Ollama RAG (`POST /api/rag/roadmap`)
   - **Similar Projects** — embedding neighbors (`POST /recommend/`)
   - **GitHub** — external link

---

## Overall Execution Flow

```
1. [ONCE]  python scraper.py     → new_data.json
2. [ONCE]  python process.py     → processed.json
3. [ONCE]  python analysis.py    → console stats (optional)
4. [SERVER] uvicorn backend.main:app --reload --port 8000
5. [UI]     cd frontend && npm run dev
6. [OPTIONAL] ollama serve       → for RAG features
```

The search index is **lazily built on the first `/search/` or `/recommend/` request** and cached in `vector_db/`.
