# RepoMind AI — Directory Structure

## Root Level

```
ir-project/
├── scraper.py                      # GitHub scraper (entry point)
├── process.py                      # NLP processing pipeline
├── analysis.py                     # Dataset statistics reporter
├── repo_utils.py                   # Shared GitHub URL/repo helpers
├── smart_profile_recommender_v2.py # Profile-based recommender + search
├── semantic_hybrid_recommender.py  # PRIMARY search engine (BM25 + semantic + CLI)
├── quadrant_updater.py             # Optional: upload processed.json to Qdrant
├── run_recommender_pipeline.py     # CLI pipeline runner for recommender
├── run_search.py                   # CLI search runner
├── index_to_qdrant.py              # Thin wrapper for Qdrant indexing
├── docker-compose.yml              # PostgreSQL service (not wired to app yet)
├── .env                            # Backend/scraper env (GITHUB_TOKEN, Qdrant, etc.)
├── .gitignore
│
├── backend/                        # FastAPI application
├── frontend/                       # React + Vite SPA
│
├── vector_db/                      # ACTIVE search index storage
├── search_index/                   # Legacy pickle-based index (deprecated)
├── qdrant_storage/                 # Local Qdrant data (if used)
│
├── data.json                       # Older raw scraped data
├── new_data.json                   # Current scraper output
├── processed.json                  # Primary NLP-processed dataset (~58 MB)
├── cache.json                      # HTTP cache from scraper
├── profile_options.json            # Older profile options (deprecated)
├── smart_profile_options.json      # Active profile wizard options
├── repo_embeddings.npy             # Root-level stale embedding copy
│
├── docs/                           # Agent-oriented documentation (this folder)
├── README.md
├── PROJECT_A_TO_Z.md
├── EXCUTION.md, Pipeline.md
├── COURSE-REQUIREMENTS.md
├── SCRAPER_DOCUMENTATION.md
├── GEMINI.md, app_arch.md
└── robots.txt
```

> **Removed since earlier versions:** Root-level `core/` and `api/` directories no longer exist. The search engine moved into `semantic_hybrid_recommender.py`. All active backend code is under `backend/`.

---

## `/backend/` — FastAPI Application

```
backend/
├── main.py                         # App factory, CORS, 7 router registrations
│
├── api/                            # Route handlers (thin — delegate to core/)
│   ├── search.py                   # POST /search/, POST /search/explain
│   ├── recommend.py                # POST /recommend/
│   ├── repos.py                    # GET /repos/, /filters/options, /details/{id}
│   ├── profile.py                  # GET /profile/questions, POST /profile/recommend|search
│   ├── advisor.py                  # POST /api/advisor/explain|roadmap|compare|summary
│   ├── project_explainer.py        # POST /api/project-explainer/explain
│   └── rag.py                      # POST /api/rag/explain|roadmap
│
├── core/                           # Business logic
│   ├── semantic_loader.py          # Singleton engine loader + search adapters
│   ├── profile_loader.py           # Profile recommender loader + normalization
│   ├── engine_loader.py            # Minimal helper
│   ├── repo_intelligence.py        # Tech stack, README sections, health scores
│   ├── repo_explainer.py           # Rule-based single-repo explanation
│   ├── project_explainer.py        # Deep README structured explanation
│   ├── roadmap_generator.py        # Goal-aware roadmap steps
│   ├── repo_comparator.py          # Side-by-side comparison
│   ├── ai_advisor.py               # Multi-repo advisory summary
│   ├── rag_advisor.py              # Ollama-grounded explain + roadmap
│   └── llm_client.py               # Ollama HTTP chat client
│
└── schemas/                        # Pydantic request/response models
    ├── search_schema.py            # SearchRequest, RecommendRequest, ExplainRequest
    ├── advisor.py                  # Advisor request models
    ├── profile_schema.py           # Profile request models
    └── project_explainer.py        # ProjectExplainRequest
```

**Root imports used by backend:** `repo_utils.py`, `semantic_hybrid_recommender.py`, `smart_profile_recommender_v2.py`

**Data dependencies:** `processed.json`, `smart_profile_options.json`, `vector_db/`

---

## `/frontend/` — React Application

```
frontend/
├── package.json
├── vite.config.js                  # Proxy /api → :8000, polling watch for USB drives
├── index.html
├── .env.development                # VITE_API_URL=/api
├── .env.example
│
└── src/
    ├── main.jsx                    # React entry
    ├── App.jsx                     # Root component (all state, main views)
    ├── App.css, index.css
    │
    ├── api/
    │   ├── client.js               # Axios + main API calls (search, profile, health)
    │   ├── advisor.js              # Rule-based advisor API (axios, VITE_API_BASE_URL)
    │   ├── projectExplainer.js     # Project explainer API
    │   └── ragAdvisor.js           # Ollama RAG API (fetch, VITE_API_BASE_URL)
    │
    ├── components/
    │   ├── SearchBar.jsx
    │   ├── Filters.jsx
    │   ├── RepoCard.jsx            # Search result card (all action buttons)
    │   ├── ProfileWizard.jsx
    │   ├── ProfileRepoCard.jsx     # Profile recommendation card (no AI buttons)
    │   ├── RecommendationPanel.jsx # Similar repos side panel
    │   ├── ProjectExplainButton.jsx    # Rule-based explainer modal
    │   ├── RagExplainButton.jsx        # Ollama explain/roadmap button
    │   ├── RagAnswerModal.jsx          # Ollama answer display modal
    │   ├── ScoreBreakdown.jsx
    │   ├── AdvisorButtons.jsx          # NOT mounted in App.jsx
    │   ├── AdvisorSummaryPanel.jsx     # NOT mounted in App.jsx
    │   ├── RepoExplainerPanel.jsx      # NOT mounted in App.jsx
    │   ├── RoadmapPanel.jsx            # NOT mounted in App.jsx
    │   ├── RepoCompareModal.jsx          # NOT mounted in App.jsx
    │   ├── EmptyState.jsx
    │   ├── LoadingState.jsx
    │   └── ThemeToggle.jsx
    │
    ├── hooks/
    │   └── useTheme.js
    │
    └── utils/
        ├── format.js
        ├── profileStorage.js       # localStorage profile persistence
        └── repoDisplay.js          # Language colors, repo name helpers
```

---

## `/vector_db/` — Active Search Index

Created automatically by `GitHubRepoSearchEngine` on first run.

```
vector_db/
├── bm25_index.json         # Serialized BM25 index
├── repo_embeddings.npy     # float32 embedding matrix (N × 384)
└── repo_metadata.json      # Dataset fingerprint + doc count
```

**Generated by:** `semantic_hybrid_recommender.py` via `backend/core/semantic_loader.py`
**Depends on:** `processed.json`

---

## `/search_index/` — Legacy (Deprecated)

Older pickle-based index from a previous system version. **Not used** by the current backend.

```
search_index/
├── bm25.pkl, bm25_corpus.pkl
├── config.json
├── document_texts.pkl
├── embeddings.npy
└── repos.pkl
```

---

## `/qdrant_storage/` — Local Qdrant Data

Only relevant if running Qdrant locally and using `quadrant_updater.py`.

---

## Data Files

| File | Size (approx) | Role |
|---|---|---|
| `processed.json` | ~58 MB | Primary indexed dataset |
| `data.json` | ~2 MB | Older raw dataset |
| `new_data.json` | varies | Scraper output (may be empty if not re-scraped) |
| `cache.json` | ~2 MB | Scraper HTTP cache |
| `smart_profile_options.json` | ~6 KB | Profile wizard dropdown options |
| `profile_options.json` | ~4 KB | Deprecated options file |

---

## Ignored / Generated Directories

| Directory | Reason |
|---|---|
| `frontend/node_modules/` | npm dependencies |
| `frontend/dist/` | Vite production build |
| `__pycache__/` | Python bytecode |
| `.git/` | Version control |
