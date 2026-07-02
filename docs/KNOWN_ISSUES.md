# RepoMind AI — Known Issues

Issues categorized as **Blocking**, **Warning**, or **Minor**.

---

## Blocking Issues

### B-01 — Must Run uvicorn from Project Root

**Files:** `backend/core/semantic_loader.py`, `backend/core/profile_loader.py`

Root-level bare imports:
```python
from repo_utils import is_github_repository
from semantic_hybrid_recommender import SemanticHybridRecommender
from smart_profile_recommender_v2 import UserProfile
```

**Trigger:** `cd backend && uvicorn main:app`
**Error:** `ModuleNotFoundError: No module named 'repo_utils'`
**Fix:** Always run from project root: `uvicorn backend.main:app --reload --port 8000`

---

### B-02 — `processed.json` Must Exist Before First Search

**Files:** `semantic_loader.py`, `profile_loader.py`

Server starts fine but crashes on first `/search/` or `/profile/` request if `processed.json` is missing.

**Error:** `FileNotFoundError: Data file not found: .../processed.json`
**Fix:** Run `python process.py` or ensure `processed.json` is in the repo.

---

### B-03 — `sentence-transformers` Required for Search

**File:** `semantic_hybrid_recommender.py`

Missing package causes ImportError on first search request.
**Fix:** `pip install sentence-transformers numpy`

---

### B-04 — Ollama Required for RAG Endpoints

**Files:** `llm_client.py`, `rag_advisor.py`

`/api/rag/explain` and `/api/rag/roadmap` fail with HTTP 500 if Ollama is not running.

**Error:** `Ollama request failed: ... Connection refused`
**Fix:** `ollama serve` and `ollama pull qwen2.5:1.5b`
**Note:** Rule-based features work without Ollama.

---

## Warning Issues

### W-01 — No `requirements.txt` in Repository

Python dependencies must be installed manually. See [CONFIGURATION.md](./CONFIGURATION.md) for the package list.

---

### W-02 — Inconsistent Frontend API Base URL Variables

| Client file | Env var | Dev behavior |
|---|---|---|
| `client.js` | `VITE_API_URL` | `/api` (uses Vite proxy) ✅ |
| `ragAdvisor.js` | `VITE_API_BASE_URL` | `http://127.0.0.1:8000` (direct) ✅ |
| `advisor.js` | `VITE_API_BASE_URL` | `http://127.0.0.1:8000` (direct) ✅ |
| `projectExplainer.js` | `VITE_API_BASE_URL` | `http://127.0.0.1:8000` (direct) ✅ |

RAG/advisor clients bypass the Vite proxy. This works in dev but is inconsistent. If backend runs on a different host/port, set **both** env vars.

---

### W-03 — Advisor UI Components Not Mounted in App.jsx

**Files:** `AdvisorButtons.jsx`, `AdvisorSummaryPanel.jsx`, `RoadmapPanel.jsx`, `RepoCompareModal.jsx`, `RepoExplainerPanel.jsx`

Backend `/api/advisor/*` endpoints are fully functional. Frontend components exist but are **not imported or rendered** in `App.jsx`. Only rule-based project explainer and Ollama RAG are wired in `RepoCard`.

---

### W-04 — Profile Cards Lack AI Action Buttons

**File:** `ProfileRepoCard.jsx`

Profile recommendation cards only show GitHub link and "Similar Projects". They do not include Explain Project, RAG, or score explain buttons (unlike `RepoCard.jsx` for search results).

---

### W-05 — Debug `print()` in Profile Recommender

**File:** `smart_profile_recommender_v2.py` (~line 553)

```python
print(f"\n[DEBUG] Cleaned/expanded query terms: {clean_terms}\n")
```

Executes on every `/profile/search` call. Pollutes server logs.

---

### W-06 — Bare `except:` in Scraper

**File:** `scraper.py`

Bare except clauses silently skip repos on unexpected errors.

---

### W-07 — Stale `search_index/` Pickle Files

Legacy index format. Not used by current backend. Could cause confusion if accidentally loaded.

---

### W-08 — Duplicate Profile Options Files

- `smart_profile_options.json` — **active**
- `profile_options.json` — deprecated, stale

---

### W-09 — Root-Level Stale `repo_embeddings.npy`

A copy exists at project root (~1.1 MB) separate from `vector_db/repo_embeddings.npy`. Backend uses `vector_db/` only.

---

### W-10 — CORS and DEBUG Not Env-Configurable

`backend/main.py` hardcodes CORS origins. Older docs reference `DEBUG` and `CORS_ORIGINS` env vars — these are **not implemented** in current code. `/docs` is always available.

---

### W-11 — PostgreSQL in docker-compose Not Connected

`docker-compose.yml` defines Postgres on port 5433 but no application code reads from it yet.

---

### W-12 — `new_data.json` May Be Empty

If scraper hasn't been run recently, `new_data.json` may contain only `[]`. The active dataset is `processed.json`.

---

### W-13 — RAG Has No Structured Response Schema

Unlike rule-based explainers that return typed JSON, RAG returns free-text `answer`. Frontend parses it heuristically (heading detection in `RagAnswerModal.jsx`). Format may vary by model.

---

## Minor Issues

### M-01 — Root README.md Partially Outdated

`README.md` references `smart_profile_recommender_v2.py` as CLI entry and omits FastAPI frontend, RAG, and current architecture. Prefer `/docs` for accurate reference.

---

### M-02 — `search_index/` Legacy Directory

Deprecated pickle-based index. Safe to ignore.

---

### M-03 — Multiple Overlapping Root Markdown Files

`EXCUTION.md`, `Pipeline.md`, `PROJECT_A_TO_Z.md`, `app_arch.md`, `GEMINI.md`, `COURSE-REQUIREMENTS.md` overlap with `/docs`. Use `/docs` for agent context.

---

### M-04 — `index_to_qdrant.py` Near-Empty Wrapper

Thin wrapper around `quadrant_updater.py`.

---

### M-05 — `ProjectExplainerModal.jsx` Unused

Modal logic is embedded inside `ProjectExplainButton.jsx`. Standalone `ProjectExplainerModal.jsx` file may be orphaned.

---

## Issue Summary

| ID | Severity | Description | Status |
|---|---|---|---|
| B-01 | Blocking | Must run uvicorn from project root | Known |
| B-02 | Blocking | `processed.json` required | Known |
| B-03 | Blocking | sentence-transformers required | Known |
| B-04 | Blocking | Ollama required for RAG | Known |
| W-01 | Warning | No requirements.txt | Documented |
| W-02 | Warning | Split VITE_API_URL vs VITE_API_BASE_URL | Known |
| W-03 | Warning | Advisor UI not in App.jsx | Known |
| W-04 | Warning | Profile cards lack AI buttons | Known |
| W-05 | Warning | Debug print in recommender | Low impact |
| W-06 | Warning | Bare except in scraper | Low impact |
| W-07 | Warning | Stale search_index/ | Deprecated |
| W-08 | Warning | Two profile options files | Low impact |
| W-09 | Warning | Stale root embeddings | Disk only |
| W-10 | Warning | CORS/DEBUG not env-based | Known |
| W-11 | Warning | Postgres not wired | Future work |
| W-12 | Warning | Empty new_data.json possible | Known |
| W-13 | Warning | RAG free-text response | By design |
| M-01 | Minor | Outdated root README | Known |
| M-02 | Minor | Legacy search_index/ | Ignore |
| M-03 | Minor | Overlapping root docs | Use /docs |
| M-04 | Minor | index_to_qdrant wrapper | No impact |
| M-05 | Minor | Orphan ProjectExplainerModal | No impact |
