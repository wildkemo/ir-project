# RepoMind AI — Configuration Reference

## Environment Variables

### Root `.env` (Backend + Scraper)

Create and edit `.env` at project root:

```env
# GitHub API (optional — raises rate limit from 60 to 5000 req/hour)
GITHUB_TOKEN=your_token_here

# Qdrant (optional — only for quadrant_updater.py)
QDRANT_URL=http://127.0.0.1:6333
QDRANT_COLLECTION=github_repos
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_SIZE=384

# Ollama RAG (optional — required for /api/rag endpoints)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b

# PostgreSQL (required for user management)
POSTGRES_USER=repomind
POSTGRES_PASSWORD=repomind123
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
POSTGRES_DB=repomind

# JWT Authentication (required for user management)
JWT_SECRET_KEY=change-this-to-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Logging
LOG_LEVEL=INFO
```

| Variable | Default | Required | Description |
|---|---|---|---|
| `GITHUB_TOKEN` | _(empty)_ | No | GitHub PAT for `scraper.py` |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | For RAG | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | For RAG | Model name in Ollama |
| `QDRANT_URL` | `http://127.0.0.1:6333` | No | Qdrant server (optional upload) |
| `QDRANT_COLLECTION` | `github_repos` | No | Qdrant collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | No | Model for Qdrant upload |
| `VECTOR_SIZE` | `384` | No | Embedding dimensions |
| `POSTGRES_*` | see `.env.example` | For auth | PostgreSQL connection |
| `JWT_SECRET_KEY` | _(required)_ | For auth | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | No | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | No | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | No | Refresh token TTL |
| `CORS_ORIGINS` | localhost:5173,... | No | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | No | Application log level |

> **Note:** `CORS_ORIGINS` is read from `.env` in `backend/main.py`. `/docs` is always enabled.

---

### Frontend Environment

Vite variables must be prefixed with `VITE_`.

| Variable | Dev default | Prod default | Used by |
|---|---|---|---|
| `VITE_API_URL` | `/api` (via proxy) | `http://127.0.0.1:8000` | `client.js` |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | `http://127.0.0.1:8000` | `advisor.js`, `ragAdvisor.js`, `projectExplainer.js` |

**`frontend/.env.development`:**
```env
VITE_API_URL=/api
```

To override, create `frontend/.env.local`:
```env
VITE_API_URL=/api
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Ports

| Service | Port | Configurable |
|---|---|---|
| FastAPI Backend | `8000` | `uvicorn backend.main:app --port <PORT>` |
| React Frontend (dev) | `5173` | `vite --port <PORT>` |
| Ollama | `11434` | `OLLAMA_BASE_URL` |
| Qdrant | `6333` | `QDRANT_URL` |
| PostgreSQL (docker-compose) | `5433` → container `5432` | `docker-compose.yml` |

---

## Python Dependencies

There is **no `requirements.txt`** in the repository. Install these packages (versions from a working environment):

```bash
pip install \
  fastapi>=0.115 \
  "uvicorn[standard]>=0.30" \
  pydantic>=2.7 \
  numpy>=2.0 \
  sentence-transformers>=3.0 \
  nltk>=3.9 \
  requests>=2.32 \
  beautifulsoup4>=4.12 \
  python-dotenv>=1.0 \
  qdrant-client>=1.9 \
  sqlalchemy>=2.0 \
  psycopg2-binary>=2.9 \
  alembic>=1.13 \
  argon2-cffi>=23.0 \
  python-jose[cryptography]>=3.3 \
  slowapi>=0.1.9 \
  email-validator>=2.0
```

NLTK data (stopwords, wordnet) downloads automatically on first `process.py` run.

---

## Paths

### Backend loaders

```python
# backend/core/semantic_loader.py
ROOT = Path(__file__).resolve().parents[2]   # project root
PROCESSED_PATH = ROOT / "processed.json"
VECTOR_DB_PATH = ROOT / "vector_db"

# backend/core/profile_loader.py
OPTIONS_PATH = ROOT / "smart_profile_options.json"
```

### Search engine index

```python
# semantic_hybrid_recommender.py → GitHubRepoSearchEngine
self.vector_db_path = Path(vector_db_path)  # default: "vector_db"
self.embeddings_file = self.vector_db_path / "repo_embeddings.npy"
self.metadata_file = self.vector_db_path / "repo_metadata.json"
self.bm25_file = self.vector_db_path / "bm25_index.json"
```

---

## Model Configuration

### Embedding Model

**Default:** `sentence-transformers/all-MiniLM-L6-v2`

Configured in `semantic_hybrid_recommender.py` → `GitHubRepoSearchEngine.__init__(model_name=...)`.

| Property | Value |
|---|---|
| Dimensions | 384 |
| Size | ~22 MB |
| Download | Automatic from Hugging Face on first run |

Changing the model invalidates cached embeddings (fingerprint mismatch → rebuild).

---

## Scoring Weights

### Hybrid Search

In `semantic_hybrid_recommender.py`:

```python
bm25_weight: float = 0.45
semantic_weight: float = 0.45
popularity_weight: float = 0.10
```

Override via CLI: `python semantic_hybrid_recommender.py --query "..." --bm25-weight 0.5`

### Profile Recommendation

In `smart_profile_recommender_v2.py`:

```python
0.25 * project_type + 0.20 * language + 0.20 * goal
+ 0.15 * level + 0.10 * repo_kind + 0.05 * complexity + 0.05 * profile_keyword
```

### Personalized Search

```python
0.60 * query + 0.10 * project_type + 0.10 * language + 0.08 * goal
+ 0.05 * level + 0.04 * repo_kind + 0.03 * complexity
```

---

## Scraper Configuration

In `scraper.py`:

```python
scraper = FastGitHubScraper(
    max_workers=4,
    delay=0.1,
    max_pages_per_topic=5,
    output_file="new_data.json",
)
```

---

## Profile Wizard Options

Static lists in `smart_profile_recommender_v2.py`:

- **PROJECT_TYPE_OPTIONS** — 9 types (web, AI/ML, data science, etc.)
- **GOAL_OPTIONS** — 5 goals (learning, contribution, use, production, portfolio)
- **LEVEL_OPTIONS** — 3 levels (beginner, intermediate, advanced)
- **REPO_KIND_OPTIONS** — 5 kinds (tutorial, library, full app, framework, research)
- **COMPLEXITY_OPTIONS** — 4 levels (small, medium, large, any)

Language options are **dynamically generated** from the dataset and cached in `smart_profile_options.json`.

---

## CORS Configuration

Configured via `CORS_ORIGINS` in `.env` (comma-separated). Default in `backend/main.py`:

```python
allow_origins=_parse_cors_origins()  # from CORS_ORIGINS env
```

---

## Vite Proxy

In `frontend/vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

**How it works:**
- `client.js` with `baseURL=/api` calls `/search/` → browser requests `/api/search/` → proxy strips `/api` → backend receives `/search/` ✅
- `ragAdvisor.js` calls `http://127.0.0.1:8000/api/rag/explain` directly (bypasses proxy) ✅
- Advisor routes at `/api/advisor/...` work when called with full URL or via double-`/api` pattern through proxy

---

## Docker Compose (PostgreSQL)

```bash
docker compose up -d
```

| Setting | Value |
|---|---|
| Image | `postgres:17` |
| Host port | `5433` |
| User / Password / DB | `repomind` / `repomind123` / `repomind` |
| Volume | `postgres_data` |

**Connected to application** — run `alembic upgrade head` and `python -m backend.database.seed_roles` after first start.

---

## Ollama Setup

```bash
# Install from https://ollama.com
ollama serve
ollama pull qwen2.5:1.5b

# Verify:
curl http://127.0.0.1:11434/api/tags
```

Recommended models (balance speed vs quality):
- `qwen2.5:1.5b` — default, fast
- `qwen2.5:3b` — better quality, slower
- `llama3.2:1b` — alternative small model
