# RepoMind AI — API Reference

Base URL: `http://127.0.0.1:8000`

Interactive Docs (when `DEBUG=true`): http://127.0.0.1:8000/docs

---

## Health / Root

### `GET /`

**Purpose:** API root — returns basic service info.

**Input:** None

**Output:**
```json
{
  "message": "Open-Source Project Search Engine API",
  "docs": "/docs",
  "health": "/health"
}
```

**Files:** `backend/main.py`

---

### `GET /health`

**Purpose:** Health check endpoint. Used by the frontend to verify the backend is reachable.

**Input:** None

**Output:**
```json
{ "status": "ok" }
```

**Files:** `backend/main.py`

---

## Search Routes (`/search`)

### `POST /search/`

**Purpose:** Hybrid BM25 + semantic search over all indexed repositories.

**Input (JSON body):**
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

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `query` | string | ✅ | — | 1–500 chars |
| `top_k` | int | No | 10 | 1–100 |
| `candidate_pool` | int | No | 200 | 10–500 |
| `language` | string | No | null | Filter by language |
| `license_name` | string | No | null | Filter by license |
| `min_stars` | int | No | null | Minimum star count |
| `topic` | string | No | null | Filter by topic |
| `profile` | object | No | null | Optional user profile for query enrichment |

**Output:**
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
      "phrase_score": 0.0,
      "metadata_score": 0.65,
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
      },
      "mode": null
    }
  ]
}
```

**Files:** `backend/api/search.py`, `backend/core/semantic_loader.py`, `core/search_engine.py`

---

### `POST /search/explain`

**Purpose:** Explain why a specific repository scored the way it did for a given query.

**Input (JSON body):**
```json
{
  "query": "machine learning",
  "repo_identifier": "owner/repo-name",
  "profile": { "language": "Python", "goal": "learning" }
}
```

| Field | Type | Required |
|---|---|---|
| `query` | string | ✅ |
| `repo_identifier` | string | ✅ |
| `profile` | object | No |

**Output:**
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

**Purpose:** Find repositories semantically similar to a given repository using embedding cosine similarity.

**Input (JSON body):**
```json
{
  "repo_identifier": "owner/repo-name",
  "top_k": 10,
  "same_language_only": false
}
```

| Field | Type | Required | Default |
|---|---|---|---|
| `repo_identifier` | string | ✅ | — |
| `top_k` | int | No | 10 |
| `same_language_only` | bool | No | false |

**Output:**
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
      "description": "...",
      "language": "Python",
      "topics": [...],
      "stars": 1200,
      "forks": 200,
      "semantic_cosine": 0.923456,
      "similarity": 0.923456
    }
  ]
}
```

**Files:** `backend/api/recommend.py`, `backend/core/semantic_loader.py`, `core/search_engine.py`

---

## Repository Routes (`/repos`)

### `GET /repos/`

**Purpose:** List repositories from the dataset (paginated by `limit`).

**Input (query params):**

| Param | Type | Default | Max |
|---|---|---|---|
| `limit` | int | 20 | 100 |

**Output:**
```json
{
  "count": 20,
  "results": [
    {
      "name": "repo-name",
      "full_name": "owner/repo-name",
      "url": "https://github.com/owner/repo-name",
      "description": "...",
      "language": "Python",
      "stars": 500,
      "forks": 80
    }
  ]
}
```

**Files:** `backend/api/repos.py`, `backend/core/repo_sanitize.py`

---

### `GET /repos/filters/options`

**Purpose:** Return available filter values (languages, licenses, topics) derived from the dataset.

**Input:** None

**Output:**
```json
{
  "languages": ["C", "C++", "Go", "JavaScript", "Python", ...],
  "licenses": ["Apache-2.0", "MIT", ...],
  "topics": ["android", "api", "deep-learning", ...]
}
```

**Files:** `backend/api/repos.py`

---

### `GET /repos/details/{repo_identifier}`

**Purpose:** Retrieve the full raw document for a specific repository.

**Input (path param):**

| Param | Type | Example |
|---|---|---|
| `repo_identifier` | string (path) | `owner/repo-name` or GitHub URL |

**Output:** Full repository document from `processed.json`.

**Error:** `404` if repository not found.

**Files:** `backend/api/repos.py`, `backend/core/semantic_loader.py`

---

## Profile Routes (`/profile`)

### `GET /profile/questions`

**Purpose:** Return the profile wizard questions and their answer options.

**Input:** None

**Output:**
```json
{
  "questions": [
    {
      "id": "project_type",
      "title": "What type of project are you looking for?",
      "allow_skip": true,
      "options": [
        { "label": "Web Development", "value": "web_dev", "count": null },
        { "label": "AI / Machine Learning", "value": "ai_ml", "count": null }
      ]
    },
    { "id": "language", "title": "Which programming language do you prefer?", "options": [...] },
    { "id": "goal", ... },
    { "id": "level", ... },
    { "id": "repo_kind", ... },
    { "id": "complexity", ... }
  ]
}
```

**Files:** `backend/api/profile.py`, `backend/core/profile_loader.py`, `smart_profile_options.json`

---

### `POST /profile/recommend`

**Purpose:** Return repositories matching a user profile (cold-start, no search query).

**Input (JSON body):**
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

All fields are optional (null skips that dimension).

**Output:**
```json
{
  "count": 10,
  "engine": "smart_profile_recommender_v2",
  "profile": { "project_type": "ai_ml", "language": "Python", ... },
  "results": [
    {
      "rank": 1,
      "score": 0.72,
      "title": "...",
      "full_name": "owner/repo",
      "url": "...",
      "description": "...",
      "language": "Python",
      "topics": [...],
      "stars": 2000,
      "forks": 300,
      "why_recommended": ["Matches your selected project type", "Matches your preferred language: Python"],
      "score_breakdown": { "project_type": 0.8, "language": 1.0, "goal": 0.6, ... },
      "mode": "profile_recommendation",
      "doc_id": 42
    }
  ]
}
```

**Files:** `backend/api/profile.py`, `backend/core/profile_loader.py`, `smart_profile_recommender_v2.py`

---

### `POST /profile/search`

**Purpose:** Hybrid personalized search — combines query relevance with user profile re-ranking.

**Input (JSON body):**
```json
{
  "query": "image processing",
  "project_type": "ai_ml",
  "language": "Python",
  "goal": "learning",
  "level": "beginner",
  "top_k": 10
}
```

| Field | Type | Required |
|---|---|---|
| `query` | string | ✅ |
| Other profile fields | optional | No |

**Output:** Same structure as `/profile/recommend`, with `mode: "personalized_search"`.

**Files:** `backend/api/profile.py`, `backend/core/profile_loader.py`, `smart_profile_recommender_v2.py`

---

## AI Advisor Routes (`/api/advisor`)

### `POST /api/advisor/explain`

**Purpose:** Generate a structured explanation for a single repository (strengths, weaknesses, best_for, roadmap).

**Input (JSON body):**
```json
{
  "repo": {
    "name": "awesome-ml",
    "full_name": "owner/awesome-ml",
    "url": "https://github.com/owner/awesome-ml",
    "description": "...",
    "language": "Python",
    "stars": 5000,
    "forks": 800,
    "topics": ["machine-learning"],
    "readme": "# README content..."
  },
  "profile": { "language": "Python", "goal": "learning", "level": "beginner" },
  "query": "machine learning",
  "score_breakdown": { "bm25": 0.85, "semantic": 0.77 },
  "include_roadmap": true
}
```

**Output:**
```json
{
  "repo_name": "awesome-ml",
  "repo_url": "https://github.com/owner/awesome-ml",
  "summary": "awesome-ml is a Python-based repository...",
  "best_for": "Learning and exploration",
  "difficulty": "beginner",
  "technologies": ["python", "tensorflow", "numpy"],
  "topics": ["machine-learning"],
  "scores": {
    "documentation_score": 0.72,
    "contribution_score": 0.45,
    "health_score": 0.68,
    "repo_intents": { "learning": 0.8, "production": 0.3, ... }
  },
  "strengths": ["Strong documentation signals", "Includes installation guidance"],
  "weaknesses": ["Limited contribution readiness signals"],
  "why_recommended": ["Relevant to the search query: 'machine learning'"],
  "roadmap": {
    "roadmap_type": "learning",
    "title": "Learning roadmap for awesome-ml",
    "steps": ["Start by reading the README...", ...]
  }
}
```

**Files:** `backend/api/advisor.py`, `backend/core/repo_explainer.py`, `backend/core/repo_intelligence.py`, `backend/core/roadmap_generator.py`

---

### `POST /api/advisor/roadmap`

**Purpose:** Generate a personalized action roadmap for a repository based on user goal.

**Input (JSON body):**
```json
{
  "repo": { ... repo object ... },
  "profile": { "goal": "contribution", "level": "intermediate" }
}
```

**Output:**
```json
{
  "roadmap_type": "contribution",
  "title": "Contribution roadmap for awesome-ml",
  "steps": [
    "Start by reading the README...",
    "Follow the installation/setup section...",
    "Read the contributing guide carefully...",
    "Look for good-first-issue, help-wanted tasks...",
    "Open a small pull request..."
  ]
}
```

**Files:** `backend/api/advisor.py`, `backend/core/roadmap_generator.py`, `backend/core/repo_intelligence.py`

---

### `POST /api/advisor/compare`

**Purpose:** Compare two repositories side-by-side and recommend the better one for the user's goal.

**Input (JSON body):**
```json
{
  "repo_a": { ... repo object ... },
  "repo_b": { ... repo object ... },
  "profile": { "goal": "learning" },
  "query": "machine learning"
}
```

**Output:**
```json
{
  "repo_a": "owner/repo-a",
  "repo_b": "owner/repo-b",
  "comparison_table": [
    { "feature": "Language", "repo_a": "Python", "repo_b": "JavaScript" },
    { "feature": "Documentation Score", "repo_a": 0.72, "repo_b": 0.45 },
    { "feature": "Stars", "repo_a": 5000, "repo_b": 1200 }
  ],
  "repo_a_goal_score": 0.68,
  "repo_b_goal_score": 0.43,
  "winner": "owner/repo-a",
  "recommendation": "For learning, owner/repo-a looks like the stronger choice...",
  "repo_a_explainer": { ... full explanation ... },
  "repo_b_explainer": { ... full explanation ... }
}
```

**Files:** `backend/api/advisor.py`, `backend/core/repo_comparator.py`, `backend/core/repo_intelligence.py`, `backend/core/repo_explainer.py`

---

### `POST /api/advisor/summary`

**Purpose:** AI Advisor summary — analyzes top search results and recommends the best repository with reasoning and roadmap.

**Input (JSON body):**
```json
{
  "query": "machine learning python",
  "profile": { "language": "Python", "goal": "learning", "level": "beginner" },
  "results": [ ... array of search result objects ... ],
  "top_k": 5
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `query` | string | ✅ | Max 500 chars |
| `profile` | object | ✅ | Can be empty `{}` |
| `results` | array | ✅ | Max 20 items |
| `top_k` | int | No | 1–20, default 5 |

**Output:**
```json
{
  "summary": "Based on the query 'machine learning python'...",
  "recommended_repo": "owner/best-repo",
  "recommended_order": ["owner/best-repo", "owner/second-repo"],
  "best_for_learning": "owner/tutorial-repo",
  "best_for_contribution": "owner/active-repo",
  "best_for_production": "owner/stable-repo",
  "roadmap_for_recommended_repo": { ... roadmap object ... },
  "top_explanations": [
    {
      "repo_name": "owner/best-repo",
      "advisor_score": 0.82,
      "score_breakdown": { ... },
      "explanation": { ... }
    }
  ]
}
```

**Files:** `backend/api/advisor.py`, `backend/core/ai_advisor.py`

---

## Project Explainer Routes (`/api/project-explainer`)

### `POST /api/project-explainer/explain`

**Purpose:** Deep analysis of a repository — README parsing, section detection, snippet extraction, full metrics.

**Input (JSON body):**
```json
{
  "repo": {
    "name": "awesome-ml",
    "url": "https://github.com/owner/awesome-ml",
    "description": "...",
    "language": "Python",
    "stars": 5000,
    "forks": 800,
    "topics": ["machine-learning"],
    "readme": "# Full README content..."
  },
  "profile": { "language": "Python", "goal": "learning" },
  "query": "machine learning"
}
```

**Output:**
```json
{
  "repo_identity": {
    "name": "awesome-ml",
    "full_name": "owner/awesome-ml",
    "url": "https://github.com/owner/awesome-ml",
    "description": "...",
    "language": "Python",
    "topics": ["machine-learning"],
    "technologies": ["python", "tensorflow", "numpy"]
  },
  "project_summary": "awesome-ml is a Python-based GitHub repository...",
  "best_for": "Learning and exploration (beginner level)",
  "difficulty": "beginner",
  "metrics": {
    "stars": 5000,
    "forks": 800,
    "contributors_count": "Not available",
    "open_issues": 42,
    "watchers": 300,
    "license": "MIT",
    "last_updated": "2024-05-01T00:00:00Z",
    "documentation_score": 0.72,
    "contribution_score": 0.45,
    "health_score": 0.68,
    "popularity_score": 0.70,
    "activity_score": 0.85
  },
  "readme_analysis": {
    "preview": "First 700 chars of clean README...",
    "detected_sections": {
      "installation": true,
      "usage": true,
      "examples": true,
      "contributing": false,
      "license": true,
      "api": false,
      "testing": false,
      "deployment": false
    },
    "section_snippets": {
      "installation": "pip install awesome-ml...",
      "usage": "import awesome_ml..."
    }
  },
  "scores_interpretation": {
    "documentation": "Strong",
    "contribution": "Medium",
    "health": "Strong",
    "activity": "Strong",
    "popularity": "Strong"
  },
  "strengths": ["Strong README/documentation signals.", "Includes installation guidance."],
  "limitations": ["Contribution-readiness signals are limited."],
  "how_to_use_it": ["Start with the Installation section...", "Follow the Usage section..."],
  "contribution_guidance": ["Check GitHub issues and repository guidelines..."],
  "why_it_matches": ["It was explained in the context of the user query: 'machine learning'."],
  "raw_scores": {}
}
```

**Files:** `backend/api/project_explainer.py`, `backend/core/project_explainer.py`
