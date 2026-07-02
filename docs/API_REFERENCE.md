# RepoMind AI — API Reference

Base URL: `http://127.0.0.1:8000`

Interactive docs: http://127.0.0.1:8000/docs (always available — no DEBUG gate in current `main.py`)

---

## Health / Root

### `GET /`

Returns basic service info.

```json
{
  "message": "Open-Source Project Search Engine API",
  "docs": "/docs",
  "health": "/health"
}
```

**File:** `backend/main.py`

---

### `GET /health`

Health check used by frontend on load.

```json
{ "status": "ok" }
```

**File:** `backend/main.py`

---

## Search Routes (`/search`)

### `POST /search/`

Hybrid BM25 + semantic search over all indexed repositories.

**Request body:**

```json
{
  "query": "machine learning python",
  "top_k": 10,
  "candidate_pool": 200,
  "language": "Python",
  "license_name": "MIT",
  "min_stars": 100,
  "topic": "deep-learning",
  "profile": {
    "project_type": "ai_ml",
    "language": "Python",
    "goal": "learning",
    "level": "beginner",
    "repo_kind": "tutorial",
    "complexity": "medium"
  }
}
```

| Field | Type | Required | Default |
|---|---|---|---|
| `query` | string | ✅ | — |
| `top_k` | int | No | 10 (1–100) |
| `candidate_pool` | int | No | 200 (10–500) |
| `language` | string | No | null |
| `license_name` | string | No | null |
| `min_stars` | int | No | null |
| `topic` | string | No | null |
| `profile` | object | No | null |

**Response:**

```json
{
  "query": "machine learning python",
  "count": 10,
  "engine": "semantic_hybrid_recommender",
  "results": [
    {
      "rank": 1,
      "score": 0.812345,
      "bm25_score": 0.85,
      "semantic_score": 0.77,
      "id": 42,
      "title": "awesome-ml",
      "full_name": "owner/awesome-ml",
      "url": "https://github.com/owner/awesome-ml",
      "description": "...",
      "language": "Python",
      "topics": ["machine-learning", "python"],
      "license": "MIT",
      "stars": 5000,
      "forks": 800,
      "why_recommended": ["BM25 matched query terms: machine, learning"],
      "score_breakdown": {
        "lexical_query_score": 0.85,
        "semantic_similarity": 0.77,
        "profile_match": 0.65,
        "weights": {"bm25": 0.45, "semantic": 0.45, "popularity": 0.10}
      }
    }
  ]
}
```

**Files:** `backend/api/search.py`, `backend/core/semantic_loader.py`, `semantic_hybrid_recommender.py`

---

### `POST /search/explain`

Explain why a specific repository scored as it did for a query.

**Request:**

```json
{
  "query": "machine learning",
  "repo_identifier": "owner/repo-name",
  "profile": { "language": "Python", "goal": "learning" }
}
```

**Response:**

```json
{
  "query": "machine learning",
  "enriched_query": "machine learning python learning tutorial",
  "repo": "owner/repo-name",
  "final_score": 0.812345,
  "bm25_contribution": 0.382,
  "semantic_contribution": 0.347,
  "profile_contribution": 0.065,
  "raw_parts": {
    "bm25_score": 0.848,
    "semantic_score": 0.771,
    "profile_score": 0.651
  },
  "why_recommended": ["BM25 matched query terms: machine, learning"]
}
```

**Files:** `backend/api/search.py`, `backend/core/semantic_loader.py`

---

## Recommendation Routes (`/recommend`)

### `POST /recommend/`

Find repositories semantically similar to a given repo (embedding cosine similarity).

**Request:**

```json
{
  "repo_identifier": "owner/repo-name",
  "top_k": 10,
  "same_language_only": false
}
```

**Response:**

```json
{
  "repo_identifier": "owner/repo-name",
  "count": 10,
  "engine": "semantic_hybrid_recommender",
  "results": [
    {
      "rank": 1,
      "doc_id": 17,
      "full_name": "other/similar-repo",
      "title": "similar-repo",
      "url": "https://github.com/other/similar-repo",
      "semantic_cosine": 0.923456,
      "similarity": 0.923456
    }
  ]
}
```

**Files:** `backend/api/recommend.py`, `backend/core/semantic_loader.py`

---

## Repository Routes (`/repos`)

### `GET /repos/`

List repositories from the dataset (paginated).

| Param | Default | Max |
|---|---|---|
| `limit` | 20 | 100 |

**Files:** `backend/api/repos.py`, `repo_utils.py`

---

### `GET /repos/filters/options`

Returns available languages, licenses, and topics from the dataset.

**Files:** `backend/api/repos.py`

---

### `GET /repos/details/{repo_identifier}`

Full raw document for a repository from `processed.json`. Returns 404 if not found.

**Files:** `backend/api/repos.py`

---

## Profile Routes (`/profile`)

### `GET /profile/questions`

Returns profile wizard questions and options from `smart_profile_options.json`.

**Files:** `backend/api/profile.py`, `backend/core/profile_loader.py`

---

### `POST /profile/recommend`

Cold-start recommendations from user profile (no search query).

**Request:**

```json
{
  "project_type": "ai_ml",
  "language": "Python",
  "goal": "learning",
  "level": "beginner",
  "repo_kind": "tutorial",
  "complexity": "medium",
  "top_k": 10
}
```

All profile fields are optional.

**Response includes:** `engine: "smart_profile_recommender_v2"`, `profile`, `results[]` with `why_recommended`, `score_breakdown`, `mode: "profile_recommendation"`

**Files:** `backend/api/profile.py`, `backend/core/profile_loader.py`, `smart_profile_recommender_v2.py`

---

### `POST /profile/search`

Hybrid personalized search combining query relevance with profile re-ranking.

**Request:** Same as recommend + required `query` field.

**Response:** Same structure with `mode: "personalized_search"`.

---

## AI Advisor Routes (`/api/advisor`) — Rule-Based

> These endpoints work but are **not mounted in the main App.jsx UI**. Frontend components exist in `frontend/src/components/Advisor*.jsx`.

### `POST /api/advisor/explain`

Structured explanation for one repository.

**Request:**

```json
{
  "repo": { "name": "...", "full_name": "...", "readme": "...", "stars": 5000 },
  "profile": { "goal": "learning", "level": "beginner" },
  "query": "machine learning",
  "score_breakdown": { "bm25": 0.85 },
  "include_roadmap": true
}
```

**Response:** `summary`, `best_for`, `difficulty`, `technologies`, `scores`, `strengths`, `weaknesses`, `why_recommended`, optional `roadmap`

**Files:** `backend/api/advisor.py`, `backend/core/repo_explainer.py`, `backend/core/repo_intelligence.py`

---

### `POST /api/advisor/roadmap`

Goal-aware step-by-step roadmap.

**Request:** `{ "repo": {...}, "profile": { "goal": "contribution" } }`

**Response:** `{ "roadmap_type", "title", "steps": [...] }`

---

### `POST /api/advisor/compare`

Side-by-side comparison of two repositories.

**Request:** `{ "repo_a": {...}, "repo_b": {...}, "profile": {...}, "query": "..." }`

**Response:** `comparison_table`, `winner`, `recommendation`, `repo_a_explainer`, `repo_b_explainer`

---

### `POST /api/advisor/summary`

Multi-repo advisory summary over search results.

**Request:** `{ "query": "...", "profile": {...}, "results": [...], "top_k": 5 }`

**Response:** `summary`, `recommended_repo`, `recommended_order`, `best_for_learning`, `roadmap_for_recommended_repo`, `top_explanations`

---

## Project Explainer Routes (`/api/project-explainer`)

### `POST /api/project-explainer/explain`

Deep rule-based README analysis. **Used by "Explain Project" button in RepoCard.**

**Request:**

```json
{
  "repo": {
    "name": "awesome-ml",
    "url": "https://github.com/owner/awesome-ml",
    "description": "...",
    "language": "Python",
    "stars": 5000,
    "topics": ["machine-learning"],
    "readme": "# Full README..."
  },
  "profile": { "goal": "learning" },
  "query": "machine learning"
}
```

**Response sections:**

- `repo_identity` — name, url, language, topics, technologies
- `project_summary`, `best_for`, `difficulty`
- `metrics` — stars, forks, documentation_score, health_score, activity_score, etc.
- `readme_analysis` — preview, detected_sections, section_snippets
- `scores_interpretation` — Strong/Medium/Limited labels
- `strengths`, `limitations`, `how_to_use_it`, `contribution_guidance`, `why_it_matches`

**Files:** `backend/api/project_explainer.py`, `backend/core/project_explainer.py`

---

## RAG Routes (`/api/rag`) — Ollama LLM

> **Requires Ollama running locally.** Used by `RagExplainButton` in RepoCard.

### `POST /api/rag/explain`

Grounded natural-language repository explanation via local Ollama model.

**Request:**

```json
{
  "repo": { "full_name": "owner/repo", "description": "...", "readme": "...", "stars": 1000 },
  "query": "machine learning",
  "profile": { "goal": "learning", "level": "beginner" }
}
```

**Response:**

```json
{
  "mode": "rag_ollama",
  "model": "qwen2.5:1.5b",
  "answer": "1. Short Summary\n...\n8. Final recommendation\n..."
}
```

The `answer` is free-text structured by the prompt (8 sections). Frontend renders it in `RagAnswerModal`.

**Files:** `backend/api/rag.py`, `backend/core/rag_advisor.py`, `backend/core/llm_client.py`

---

### `POST /api/rag/roadmap`

Grounded learning/usage roadmap via Ollama.

**Request:** Same shape as `/api/rag/explain`.

**Response:**

```json
{
  "mode": "rag_ollama",
  "model": "qwen2.5:1.5b",
  "answer": "1. Roadmap Goal\n...\n8. Next step\n..."
}
```

**Files:** `backend/api/rag.py`, `backend/core/rag_advisor.py`

---

## Error Handling

All routes use FastAPI `HTTPException`:

| Code | When |
|---|---|
| 404 | Repository not found (`/search/explain`, `/repos/details/`) |
| 500 | Engine errors, missing `processed.json`, Ollama unreachable |

Ollama failures surface as 500 with message like: `Ollama request failed: 404 ...`

---

## Frontend API Client Mapping

| Client file | Base URL env var | Used by |
|---|---|---|
| `client.js` | `VITE_API_URL` (dev: `/api` via proxy) | App.jsx, SearchBar, RepoCard (explain) |
| `projectExplainer.js` | `VITE_API_BASE_URL` or localhost:8000 | ProjectExplainButton |
| `ragAdvisor.js` | `VITE_API_BASE_URL` or localhost:8000 | RagExplainButton |
| `advisor.js` | `VITE_API_BASE_URL` or localhost:8000 | AdvisorButtons (unused in App) |
