# RepoMind AI — Directory Structure

## Root Level

```
RepoMind AI/
├── scraper.py                  # [DATA] GitHub scraper (entry point)
├── process.py                  # [DATA] NLP processing pipeline
├── analysis.py                 # [DATA] Dataset statistics reporter
├── repo_utils.py               # [SHARED] GitHub URL/repo helpers (shared by backend + scripts)
├── smart_profile_recommender_v2.py  # [CORE] Profile-based BM25 recommender
├── semantic_hybrid_recommender.py   # [ALIAS] see core/search_engine.py note
├── quadrant_updater.py         # [OPTIONAL] Upload processed.json to Qdrant
├── run_recommender_pipeline.py # [UTIL] Pipeline runner for recommender
├── run_search.py               # [UTIL] CLI search runner
├── index_to_qdrant.py          # [UTIL] Thin wrapper for Qdrant indexing
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore
│
├── backend/                    # FastAPI application package
├── core/                       # Standalone copies of engine modules (older layer)
├── api/                        # Older API layer (pre-backend refactor)
├── frontend/                   # React + Vite single-page application
├── pipelines/                  # Empty (placeholder for future pipeline modules)
│
├── storage/                    # ACTIVE search index storage (used by backend)
├── vector_db/                  # Alternative index location
├── search_index/               # Older/alternative search index (may be stale)
├── qdrant_storage/             # Local Qdrant data directory
│
├── data.json                   # Raw scraped data (older dataset)
├── new_data.json               # Raw scraped data (current scraper output)
├── processed.json              # Processed NLP data (primary dataset)
├── cache.json                  # HTTP cache from scraper
├── profile_options.json        # Profile wizard options (older version)
├── smart_profile_options.json  # Profile wizard options (current, auto-generated)
├── repo_embeddings.npy         # Root-level copy of embeddings (may be stale)
│
├── README.md
├── EXCUTION.md                 # Execution guide (original)
├── GEMINI.md                   # Project rules for AI assistant
├── COURSE-REQUIREMENTS.md      # Course requirements
├── Pipeline.md                 # Pipeline documentation
├── PROJECT_A_TO_Z.md           # Comprehensive project guide
├── app_arch.md                 # Architecture notes
├── SCRAPER_DOCUMENTATION.md    # Scraper documentation
└── robots.txt                  # robots.txt compliance reference
```

---

## `/backend/` — FastAPI Application

**Purpose:** The main deployable backend. All FastAPI routes, schemas, and core service modules are here.

```
backend/
├── __init__.py
├── main.py                     # FastAPI app factory, CORS, router inclusion
│
├── api/                        # Route handlers (thin — delegate to core/)
│   ├── __init__.py
│   ├── search.py               # POST /search/, POST /search/explain
│   ├── recommend.py            # POST /recommend/
│   ├── repos.py                # GET /repos/, /repos/filters/options, /repos/details/{id}
│   ├── profile.py              # GET /profile/questions, POST /profile/recommend, /profile/search
│   ├── advisor.py              # POST /api/advisor/explain|roadmap|compare|summary
│   └── project_explainer.py   # POST /api/project-explainer/explain
│
├── core/                       # Business logic and AI services
│   ├── __init__.py
│   ├── semantic_loader.py      # Singleton engine loader + search/recommend adapters
│   ├── profile_loader.py       # Profile recommender loader + normalization
│   ├── engine_loader.py        # (Minimal helper)
│   ├── http_errors.py          # Error helper functions
│   ├── repo_sanitize.py        # Public repo summary (safe fields only)
│   ├── repo_intelligence.py    # Enrichment: tech stack, README sections, health scores
│   ├── repo_explainer.py       # Explanation generation for a single repo
│   ├── project_explainer.py    # Deep README analysis + full structured explanation
│   ├── roadmap_generator.py    # Goal-aware roadmap generation
│   ├── repo_comparator.py      # Side-by-side repo comparison
│   └── ai_advisor.py           # Multi-repo advisory + best-repo selection
│
└── schemas/                    # Pydantic request/response models
    ├── __init__.py
    ├── search_schema.py        # SearchRequest, RecommendRequest, ExplainRequest
    ├── advisor.py              # ExplainRepoRequest, RoadmapRequest, CompareReposRequest, AdvisorSummaryRequest
    ├── profile_schema.py       # ProfileRecommendRequest, ProfileSearchRequest
    ├── project_explainer.py    # ProjectExplainRequest
    └── validators.py           # Shared field validators
```

**Dependencies:** Imports from root-level `repo_utils.py`, `smart_profile_recommender_v2.py`, and `core/search_engine.py` (via `semantic_hybrid_recommender` alias).

**Connects to:** `storage/` (search index), `processed.json` (dataset), `smart_profile_options.json`.

---

## `/core/` — Standalone Engine Layer

**Purpose:** Original engine modules that exist independently of FastAPI. Contains standalone versions of the search engine and related utilities.

> **Note:** Many files in `/core/` are duplicates or older versions of files in `/backend/core/`. The `backend/core/` versions are the **active** ones used by the running server.

```
core/
├── __init__.py
├── search_engine.py            # [PRIMARY] GitHubRepoSearchEngine (BM25 + semantic)
├── engine_loader.py            # Thin loader for search engine
├── hybrid_ranker.py            # (Stub/placeholder, 57 bytes)
├── recommender.py              # (Stub/placeholder, 57 bytes)
├── profile_engine.py           # Large profile engine (may be an older version of smart_profile_recommender_v2.py)
├── profile_loader.py           # Profile loader (copy of backend/core/profile_loader.py)
├── project_explainer.py        # Project explainer (copy of backend/core/project_explainer.py)
├── http_errors.py              # HTTP error helpers
├── rag_advisor.py              # RAG advisor (experimental/unused)
├── repo_comparator.py          # Repo comparator
├── repo_explainer.py           # Repo explainer
├── repo_intelligence.py        # Repo intelligence
├── repo_sanitize.py            # Repo sanitizer
├── repo_utils.py               # Repo utilities (copy of root repo_utils.py)
├── roadmap_generator.py        # Roadmap generator
└── semantic_loader.py          # Semantic loader
```

**Classification:** Mostly **Supporting/Duplicate** — see `FILE_REFERENCE.md` for classification details.

---

## `/api/` — Old API Layer

**Purpose:** An older API layer that existed before the `backend/` package was created. Appears to be a structural precursor.

```
api/
├── __init__.py
├── explain.py                  # Old explain route handler
├── recommend.py                # Old recommend route handler
├── search.py                   # Old search route handler
│
└── schemas/
    ├── __init__.py
    ├── advisor.py              # Old advisor schema
    ├── profile_schema.py       # Old profile schema
    ├── project_explainer.py    # Old project explainer schema
    ├── search_schema.py        # Old search schema
    └── validators.py           # Old validators
```

**Classification:** **Deprecated/Unused** — the active API is in `backend/api/`.

---

## `/frontend/` — React Application

**Purpose:** The complete single-page web application.

```
frontend/
├── package.json                # Dependencies (React 19, Vite 8, Axios, Lucide React)
├── vite.config.js              # Vite config with proxy → :8000, watch settings
├── index.html                  # HTML entry point
├── .env.development            # Dev env (VITE_API_URL=/api via proxy)
├── .env.example                # Env variable template
│
└── src/
    ├── main.jsx                # React entry point
    ├── App.jsx                 # Root component (all state, routing logic)
    ├── App.css                 # Main stylesheet
    ├── index.css               # Global CSS reset + design tokens
    │
    ├── api/
    │   ├── client.js           # Axios instance + all API call functions
    │   ├── advisor.js          # Thin re-export for advisor calls
    │   └── projectExplainer.js # Thin re-export for project explainer calls
    │
    ├── components/
    │   ├── SearchBar.jsx       # Search input + submit
    │   ├── Filters.jsx         # Language/license/topic/star filters
    │   ├── RepoCard.jsx        # Individual result card with actions
    │   ├── ProfileWizard.jsx   # Multi-step profile questionnaire
    │   ├── ProfileRepoCard.jsx # Card variant for profile recommendations
    │   ├── RecommendationPanel.jsx     # Similar repos panel
    │   ├── RepoExplainerPanel.jsx      # Inline explainer panel (advisor explain)
    │   ├── ProjectExplainButton.jsx    # Button + modal trigger for project explainer
    │   ├── ProjectExplainerModal.jsx   # Full project explanation modal
    │   ├── AdvisorSummaryPanel.jsx     # AI Advisor summary display
    │   ├── AdvisorButtons.jsx          # Advisor action buttons
    │   ├── RoadmapPanel.jsx            # Roadmap step display
    │   ├── RepoCompareModal.jsx        # Repo comparison modal
    │   ├── ScoreBreakdown.jsx          # BM25/semantic/profile score display
    │   ├── EmptyState.jsx              # Empty results display
    │   ├── LoadingState.jsx            # Loading indicator
    │   └── ThemeToggle.jsx             # Dark/light mode toggle
    │
    ├── hooks/
    │   └── useTheme.js         # Dark/light theme persistence hook
    │
    └── utils/
        ├── format.js           # Number/date formatting helpers
        ├── profileStorage.js   # LocalStorage profile persistence
        └── repoDisplay.js      # Repo display helpers (language colors, etc.)
```

**Dependencies:** Node.js, npm. Connects to backend via `VITE_API_URL` (defaults to proxy at `/api` in dev, `http://127.0.0.1:8000` in prod).

---

## `/storage/` — Active Search Index (Primary)

**Purpose:** Cache directory for the active search engine indexes. Created automatically by `GitHubRepoSearchEngine` on first run.

```
storage/
├── bm25_index.json             # Serialized BM25 index (~4.5 MB)
├── repo_embeddings.npy         # NumPy float32 embedding matrix (~2.4 MB)
└── repo_metadata.json          # Fingerprint + doc count for cache invalidation
```

**Generated by:** `backend/core/semantic_loader.py` → `GitHubRepoSearchEngine`
**Depends on:** `processed.json`

---

## `/vector_db/` — Alternative Index Location

**Purpose:** A secondary index directory used when running `core/search_engine.py` directly or as an alternative path. Contains same structure as `/storage/`.

```
vector_db/
├── bm25_index.json
├── repo_embeddings.npy
└── repo_metadata.json
```

---

## `/search_index/` — Legacy Search Index

**Purpose:** Older serialized search index using pickle format. Likely generated by an older version of the system.

```
search_index/
├── bm25.pkl                    # BM25 object (pickle)
├── bm25_corpus.pkl             # BM25 corpus (pickle)
├── config.json                 # Index configuration
├── document_texts.pkl          # Document texts (pickle)
├── embeddings.npy              # Small embeddings (~45 KB, possibly subset)
└── repos.pkl                   # Repository data (pickle)
```

**Classification:** **Deprecated** — the backend uses `storage/` not `search_index/`.

---

## `/pipelines/` — Empty Placeholder

**Purpose:** Reserved for future pipeline modules. Currently contains only `__init__.py`.

---

## `/qdrant_storage/` — Local Qdrant Data

**Purpose:** Local Qdrant vector database storage (used when running Qdrant locally). Only relevant if `quadrant_updater.py` has been run.

---

## Ignored Directories

| Directory | Reason Ignored |
|---|---|
| `frontend/node_modules/` | npm dependencies |
| `frontend/dist/` | Vite production build output |
| `frontend/public/` | Static assets |
| `__pycache__/` | Python bytecode cache |
