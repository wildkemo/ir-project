# RepoMind AI — Dependency Graph

## Internal Module Dependency Map

```mermaid
graph TD
    subgraph "Data Pipeline (Root)"
        scraper[scraper.py]
        process[process.py]
        analysis[analysis.py]
        repo_utils[repo_utils.py]
        smart_profile[smart_profile_recommender_v2.py]
        search_engine[semantic_hybrid_recommender.py<br>GitHubRepoSearchEngine + BM25Index]
    end

    subgraph "Backend Entry"
        main[backend/main.py]
    end

    subgraph "Backend API"
        api_search[api/search.py]
        api_recommend[api/recommend.py]
        api_repos[api/repos.py]
        api_profile[api/profile.py]
        api_advisor[api/advisor.py]
        api_project[api/project_explainer.py]
        api_rag[api/rag.py]
    end

    subgraph "Backend Core"
        semantic_loader[semantic_loader.py]
        profile_loader[profile_loader.py]
        repo_intelligence[repo_intelligence.py]
        repo_explainer[repo_explainer.py]
        project_explainer[project_explainer.py]
        roadmap_generator[roadmap_generator.py]
        ai_advisor[ai_advisor.py]
        repo_comparator[repo_comparator.py]
        rag_advisor[rag_advisor.py]
        llm_client[llm_client.py]
    end

    subgraph "Frontend (active)"
        app[App.jsx]
        client[api/client.js]
        rag_client[api/ragAdvisor.js]
        project_client[api/projectExplainer.js]
        repo_card[RepoCard.jsx]
    end

    main --> api_search & api_recommend & api_repos & api_profile & api_advisor & api_project & api_rag

    api_search --> semantic_loader
    api_recommend --> semantic_loader
    api_repos --> semantic_loader
    api_repos --> repo_utils
    api_profile --> profile_loader
    api_advisor --> ai_advisor & repo_explainer & roadmap_generator & repo_comparator
    api_project --> project_explainer
    api_rag --> rag_advisor

    semantic_loader --> search_engine & repo_utils & smart_profile
    profile_loader --> smart_profile & repo_utils

    repo_explainer --> repo_intelligence & roadmap_generator
    ai_advisor --> repo_intelligence & repo_explainer & roadmap_generator
    repo_comparator --> repo_intelligence & repo_explainer
    roadmap_generator --> repo_intelligence
    rag_advisor --> llm_client

    app --> client & repo_card
    repo_card --> rag_client & project_client
    client --> api_search
    rag_client --> api_rag
```

---

## Textual Dependency List

### `backend/main.py`
- **Imports:** all 7 `backend/api/*` routers
- **Used by:** uvicorn entry point

### `backend/api/search.py`
- **Imports:** `semantic_loader`, `search_schema`
- **Used by:** `main.py`

### `backend/api/recommend.py`
- **Imports:** `semantic_loader`, `search_schema`
- **Used by:** `main.py`

### `backend/api/repos.py`
- **Imports:** `semantic_loader`, `repo_utils` (root)
- **Used by:** `main.py`

### `backend/api/profile.py`
- **Imports:** `profile_loader`, `profile_schema`
- **Used by:** `main.py`

### `backend/api/advisor.py`
- **Imports:** `ai_advisor`, `repo_explainer`, `roadmap_generator`, `repo_comparator`, `advisor` schema
- **Used by:** `main.py`

### `backend/api/project_explainer.py`
- **Imports:** `project_explainer`, `project_explainer` schema
- **Used by:** `main.py`

### `backend/api/rag.py`
- **Imports:** `rag_advisor`
- **Used by:** `main.py`

### `backend/core/semantic_loader.py`
- **Imports:** `repo_utils`, `semantic_hybrid_recommender`, `smart_profile_recommender_v2` (all root-level)
- **Used by:** search, recommend, repos APIs

### `backend/core/profile_loader.py`
- **Imports:** `smart_profile_recommender_v2`, `repo_utils`
- **Used by:** profile API

### `backend/core/rag_advisor.py`
- **Imports:** `llm_client`
- **Used by:** rag API

### `backend/core/llm_client.py`
- **Imports:** `requests`, `os` (stdlib)
- **External:** Ollama HTTP API at `:11434`
- **Used by:** `rag_advisor`

### `backend/core/repo_intelligence.py`
- **Imports:** stdlib only (`re`, `math`, `datetime`)
- **Used by:** repo_explainer, roadmap_generator, ai_advisor, repo_comparator

### `backend/core/project_explainer.py`
- **Imports:** stdlib only — self-contained
- **Used by:** project_explainer API

### `semantic_hybrid_recommender.py` (root)
- **Imports:** `numpy`, `sentence_transformers`, stdlib
- **Exports:** `GitHubRepoSearchEngine`, `BM25Index`, `SemanticHybridRecommender` (alias)
- **Used by:** `semantic_loader`

### `smart_profile_recommender_v2.py` (root)
- **Imports:** stdlib only
- **Used by:** `semantic_loader`, `profile_loader`

### `repo_utils.py` (root)
- **Imports:** stdlib only
- **Used by:** `semantic_loader`, `profile_loader`, repos API

---

## Circular Dependency Analysis

**No circular dependencies found.**

Flow is strictly one-directional:

```
Frontend → API routes → Core services → Root modules → Third-party / Ollama
```

---

## External Dependencies

### Python

| Package | Version (tested) | Used by |
|---|---|---|
| `fastapi` | 0.136+ | All API routes |
| `uvicorn[standard]` | 0.47+ | Process runner |
| `pydantic` | 2.12+ | All schemas |
| `numpy` | 2.4+ | `semantic_hybrid_recommender.py` |
| `sentence-transformers` | 5.5+ | Search engine embeddings |
| `nltk` | 3.9+ | `process.py` |
| `requests` | 2.32+ | `scraper.py`, `llm_client.py` |
| `beautifulsoup4` | 4.14+ | `scraper.py` |
| `python-dotenv` | 1.2+ | `scraper.py`, `quadrant_updater.py` |
| `qdrant-client` | 1.18+ | `quadrant_updater.py` (optional) |

### External Services

| Service | Port | Used by |
|---|---|---|
| Ollama | 11434 | `llm_client.py` → RAG endpoints |
| Qdrant | 6333 | `quadrant_updater.py` (optional) |
| PostgreSQL | 5433 | `docker-compose.yml` (not wired) |

### Frontend (npm)

| Package | Version | Used by |
|---|---|---|
| `react` | ^19.2 | All components |
| `react-dom` | ^19.2 | `main.jsx` |
| `axios` | ^1.16 | `client.js`, `advisor.js` |
| `lucide-react` | ^1.16 | UI icons |
| `vite` | ^8.0 | Build tool |
| `@vitejs/plugin-react` | ^6.0 | Vite plugin |

---

## Import Constraint (Critical)

Root-level modules (`repo_utils`, `semantic_hybrid_recommender`, `smart_profile_recommender_v2`) are imported with **bare names** (not package-relative). This requires:

```bash
# CORRECT — from project root
uvicorn backend.main:app --reload --port 8000

# WRONG — will fail with ModuleNotFoundError
cd backend && uvicorn main:app
```
