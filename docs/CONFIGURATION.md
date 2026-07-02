# RepoMind AI — Configuration Reference

## Environment Variables

### Root `.env` (Backend + Scraper)

Create from `.env.example`:

```bash
cp .env.example .env
```

| Variable | Default | Required | Description |
|---|---|---|---|
| `DEBUG` | `true` | No | When `true`, enables `/docs`, `/redoc`, `/openapi.json` endpoints. Set to `false` in production. |
| `CORS_ORIGINS` | `http://localhost:5173, http://127.0.0.1:5173, http://localhost:3000, http://127.0.0.1:3000` | No | Comma-separated list of allowed frontend origins for CORS. |
| `GITHUB_TOKEN` | _(empty)_ | No | GitHub Personal Access Token. Raises API rate limit from 60 to 5000 req/hour for `scraper.py`. |

### Frontend `.env` / `.env.local`

The frontend reads Vite environment variables (must be prefixed with `VITE_`).

| Variable | Default (dev) | Default (prod) | Description |
|---|---|---|---|
| `VITE_API_URL` | `/api` (proxied to `:8000`) | `http://127.0.0.1:8000` | Backend API base URL. |

To override, create `frontend/.env.local`:

```env
VITE_API_URL=http://your-backend-host:8000
```

---

## Ports

| Service | Port | Configurable? |
|---|---|---|
| FastAPI Backend | `8000` | Yes — `uvicorn backend.main:app --port <PORT>` |
| React Frontend (dev) | `5173` | Yes — `vite --port <PORT>` |
| Qdrant Vector DB | `6333` | Yes — `QDRANT_URL` env var |
| Qdrant gRPC | `6334` | Yes — Qdrant config |

---

## Paths

### Backend Core Paths

Defined in `backend/core/semantic_loader.py`:

```python
ROOT = Path(__file__).resolve().parents[2]   # = project root
PROCESSED_PATH = ROOT / "processed.json"     # dataset
VECTOR_DB_PATH = ROOT / "vector_db"          # index storage (secondary)
```

Defined in `backend/core/profile_loader.py`:

```python
ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = ROOT / "processed.json"
OPTIONS_PATH = ROOT / "smart_profile_options.json"
```

### Search Engine Index Paths

Defined in `core/search_engine.py` (`GitHubRepoSearchEngine.__init__`):

```python
self.vector_db_path = Path(vector_db_path)      # default: "storage"
self.embeddings_file = self.vector_db_path / "repo_embeddings.npy"
self.metadata_file = self.vector_db_path / "repo_metadata.json"
self.bm25_file = self.vector_db_path / "bm25_index.json"
```

The backend uses `VECTOR_DB_PATH = ROOT / "vector_db"` (note: `vector_db/`, not `storage/`).
There are two index directories (`storage/` and `vector_db/`) — both may contain indexes depending on how the engine was invoked.

---

## Model Configuration

### Embedding Model

**Default:** `sentence-transformers/all-MiniLM-L6-v2`

Configured in `core/search_engine.py`:

```python
class GitHubRepoSearchEngine:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        ...
    )
```

- **Vector dimensions:** 384
- **Model size:** ~22 MB
- **Downloads automatically** from Hugging Face on first run

To use a different model, pass it as a parameter or modify `VECTOR_DB_PATH` in `semantic_loader.py`:

```python
_hybrid = SemanticHybridRecommender(
    data_path=str(PROCESSED_PATH),
    vector_db_path=str(VECTOR_DB_PATH),
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # change here
)
```

> **Warning:** Changing the model invalidates the cached embeddings. The index will be rebuilt.

---

## Scoring Weights

### Hybrid Search (BM25 + Semantic + Popularity)

Configured in `core/search_engine.py`:

```python
bm25_weight: float = 0.45
semantic_weight: float = 0.45
popularity_weight: float = 0.10
```

Can be overridden via CLI (`--bm25-weight`, `--semantic-weight`, `--popularity-weight`) or by modifying `semantic_loader.py`.

### Profile Recommendation Weights

Configured in `smart_profile_recommender_v2.py`:

```python
final_score = (
    0.25 * project_type_score +
    0.20 * language_score +
    0.20 * goal_score +
    0.15 * level_score +
    0.10 * repo_kind_score +
    0.05 * complexity_score +
    0.05 * profile_keyword_score
)
```

### Personalized Search Weights (query + profile)

```python
final_score = (
    0.60 * query_relevance +
    0.10 * project_type +
    0.10 * language +
    0.08 * goal +
    0.05 * level +
    0.04 * repo_kind +
    0.03 * complexity
)
```

---

## Qdrant Configuration (Optional)

Configured in `quadrant_updater.py` (via environment variables or defaults):

| Variable | Default | Description |
|---|---|---|
| `QDRANT_URL` | `http://127.0.0.1:6333` | Qdrant server URL |
| `QDRANT_COLLECTION` | `github_repos` | Collection name |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model for Qdrant upload |
| `VECTOR_SIZE` | `384` | Embedding dimensions |
| `PROCESSED_FILE` | `processed.json` | Source data file |
| `QDRANT_BATCH_SIZE` | `64` | Upload batch size |

---

## Scraper Configuration

Configured in `scraper.py`:

```python
scraper = FastGitHubScraper(
    max_workers=4,           # parallel download threads
    delay=0.1,               # seconds between HTML page requests
    max_pages_per_topic=5,   # pages crawled per GitHub topic
    output_file="new_data.json",
)
```

---

## Profile Wizard Options

Configured in `smart_profile_recommender_v2.py` (static lists):

- `PROJECT_TYPE_OPTIONS` — 9 project types (web, AI/ML, data science, etc.)
- `GOAL_OPTIONS` — 5 user goals (learning, contribution, use, production, portfolio)
- `LEVEL_OPTIONS` — 3 skill levels (beginner, intermediate, advanced)
- `REPO_KIND_OPTIONS` — 5 repo kinds (tutorial, library, full app, framework, research)
- `COMPLEXITY_OPTIONS` — 4 complexity levels (small, medium, large, any)

Language options are **dynamically generated** from the dataset by `DatasetOptionsBuilder.build_language_options()` and cached in `smart_profile_options.json`.

---

## CORS Configuration

Configured in `backend/main.py`:

```python
_DEFAULT_CORS = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "http://localhost:3000,"
    "http://127.0.0.1:3000"
)
_CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _DEFAULT_CORS).split(",")
    if origin.strip()
]
```

Override with the `CORS_ORIGINS` environment variable (comma-separated).

---

## Vite Proxy Configuration

Configured in `frontend/vite.config.js`:

```javascript
server: {
    proxy: {
        '/api': {
            target: 'http://127.0.0.1:8000',
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/api/, ''),
        },
    },
}
```

All frontend API calls to `/api/...` are proxied to the backend, stripping the `/api` prefix.

Example: `POST /api/advisor/explain` → `POST http://127.0.0.1:8000/advisor/explain`

> **Note:** The `/api/advisor/` and `/api/project-explainer/` routes include `/api` in their actual FastAPI prefix. The Vite proxy strips the leading `/api`, so the frontend must use `/api/api/advisor/...` or rely on how `client.js` handles this.
> 
> Looking at `client.js`, it calls `api.post('/api/advisor/explain', ...)` where `api` has `baseURL = /api`. This means the actual URL becomes `/api/api/advisor/explain`, which the proxy rewrites to `/api/advisor/explain`. This matches the FastAPI route prefix `prefix="/api/advisor"`. This works correctly.
