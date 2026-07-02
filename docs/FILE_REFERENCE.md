# RepoMind AI — File Reference

## Classification Key

- **Core** — Required for the system to function
- **Supporting** — Helper/utility used by Core modules
- **UI-Inactive** — Frontend component exists but not mounted in App.jsx
- **Experimental** — Exists but optional / not in main flow
- **Deprecated** — Superseded or unused

---

## Root-Level Scripts

| File | Purpose | Key symbols | Used by | Classification |
|---|---|---|---|---|
| `scraper.py` | GitHub topic crawler + API repo fetcher | `FastGitHubScraper`, `run()` | Manual execution | **Core** |
| `process.py` | NLP pipeline: tokenize, normalize, score | `process_data()`, `clean_text()` | Manual execution | **Core** |
| `analysis.py` | Dataset statistics | `run_analysis()` | Manual execution | **Core** |
| `repo_utils.py` | GitHub URL validation, doc helpers | `is_github_repository()`, `repository_docs()` | backend loaders, repos API | **Core** |
| `smart_profile_recommender_v2.py` | Profile recommender + wizard options | `UserProfile`, `SmartProfileRecommender` | profile_loader, semantic_loader | **Core** |
| `semantic_hybrid_recommender.py` | Hybrid search engine + BM25 + CLI | `GitHubRepoSearchEngine`, `BM25Index`, `SemanticHybridRecommender` | semantic_loader | **Core** |
| `quadrant_updater.py` | Upload to Qdrant vector DB | `sync_processed_json_to_qdrant()` | Manual (optional) | **Experimental** |
| `run_recommender_pipeline.py` | CLI recommender runner | — | Manual | **Supporting** |
| `run_search.py` | CLI search runner | — | Manual | **Supporting** |
| `index_to_qdrant.py` | Qdrant wrapper | — | Manual | **Supporting** |
| `docker-compose.yml` | PostgreSQL 17 service | — | Manual | **Experimental** |

---

## `backend/main.py`

| File | Purpose | Key symbols | Classification |
|---|---|---|---|
| `backend/main.py` | FastAPI app, CORS, 7 routers | `app`, `health_check()` | **Core** |

Registers: search, recommend, repos, profile, advisor, project_explainer, **rag**

---

## `backend/api/`

| File | Routes | Delegates to | Classification |
|---|---|---|---|
| `search.py` | `POST /search/`, `/search/explain` | `semantic_loader` | **Core** |
| `recommend.py` | `POST /recommend/` | `semantic_loader` | **Core** |
| `repos.py` | `GET /repos/`, `/filters/options`, `/details/{id}` | `semantic_loader`, `repo_utils` | **Core** |
| `profile.py` | `GET /profile/questions`, `POST /profile/recommend`, `/profile/search` | `profile_loader` | **Core** |
| `advisor.py` | `POST /api/advisor/explain\|roadmap\|compare\|summary` | ai_advisor, repo_explainer, etc. | **Core** (API only) |
| `project_explainer.py` | `POST /api/project-explainer/explain` | `project_explainer` | **Core** |
| `rag.py` | `POST /api/rag/explain`, `/api/rag/roadmap` | `rag_advisor` | **Core** |

---

## `backend/core/`

| File | Purpose | Key symbols | Used by | Classification |
|---|---|---|---|---|
| `semantic_loader.py` | Singleton engine + search adapters | `load_semantic_hybrid()`, `hybrid_search()`, `explain_result()` | search, recommend, repos APIs | **Core** |
| `profile_loader.py` | Profile recommender singleton | `load_profile_recommender()`, `recommend_for_profile()` | profile API | **Core** |
| `repo_intelligence.py` | Repo enrichment | `enrich_repo()`, `extract_tech_stack()`, `compute_health_score()` | advisor, explainer, comparator | **Core** |
| `repo_explainer.py` | Rule-based explanation | `explain_repo()`, `build_summary()` | advisor API | **Core** |
| `project_explainer.py` | Deep README analysis | `explain_project()`, `extract_section_snippets()` | project_explainer API | **Core** |
| `roadmap_generator.py` | Goal-aware roadmaps | `generate_roadmap()` | advisor, repo_explainer | **Core** |
| `ai_advisor.py` | Multi-repo advisory | `advise()`, `_advisor_score()` | advisor API | **Core** |
| `repo_comparator.py` | Side-by-side compare | `compare_repos()` | advisor API | **Core** |
| `rag_advisor.py` | Ollama RAG explain/roadmap | `explain_repo_with_rag()`, `build_repo_context()` | rag API | **Core** |
| `llm_client.py` | Ollama HTTP client | `LLMClient.generate()` | rag_advisor | **Core** |
| `engine_loader.py` | Thin wrapper | — | minimal | **Supporting** |

---

## `backend/schemas/`

| File | Models | Classification |
|---|---|---|
| `search_schema.py` | `SearchRequest`, `RecommendRequest`, `ExplainRequest`, `ProfileContext` | **Core** |
| `advisor.py` | `ExplainRepoRequest`, `RoadmapRequest`, `CompareReposRequest`, `AdvisorSummaryRequest` | **Core** |
| `profile_schema.py` | `ProfileRecommendRequest`, `ProfileSearchRequest` | **Core** |
| `project_explainer.py` | `ProjectExplainRequest` | **Core** |

> Note: `validators.py` and `http_errors.py` referenced in older docs **no longer exist**. Validation is inline in Pydantic models; errors use `HTTPException` directly in API routes.

---

## `frontend/src/` — Active in App.jsx

| File | Purpose | Classification |
|---|---|---|
| `main.jsx` | React entry | **Core** |
| `App.jsx` | Root state, profile + search + recommendations | **Core** |
| `api/client.js` | Axios client: search, profile, health, recommend | **Core** |
| `api/projectExplainer.js` | Project explainer calls | **Core** |
| `api/ragAdvisor.js` | Ollama RAG calls (fetch-based) | **Core** |
| `components/SearchBar.jsx` | Search input | **Core** |
| `components/Filters.jsx` | Language/license/topic/star filters | **Core** |
| `components/RepoCard.jsx` | Search result card with all actions | **Core** |
| `components/ProfileWizard.jsx` | Profile questionnaire | **Core** |
| `components/ProfileRepoCard.jsx` | Profile recommendation card | **Core** |
| `components/RecommendationPanel.jsx` | Similar repos panel | **Core** |
| `components/ProjectExplainButton.jsx` | Rule-based explainer modal | **Core** |
| `components/RagExplainButton.jsx` | Ollama explain/roadmap trigger | **Core** |
| `components/RagAnswerModal.jsx` | Ollama answer display | **Core** |
| `components/ScoreBreakdown.jsx` | Score component display | **Supporting** |
| `components/ThemeToggle.jsx` | Dark/light toggle | **Supporting** |
| `components/EmptyState.jsx` | Empty/initial states | **Supporting** |
| `components/LoadingState.jsx` | Loading spinner | **Supporting** |
| `hooks/useTheme.js` | Theme persistence | **Supporting** |
| `utils/format.js` | Number formatting | **Supporting** |
| `utils/profileStorage.js` | localStorage profile | **Supporting** |
| `utils/repoDisplay.js` | Display helpers | **Supporting** |

---

## `frontend/src/` — UI-Inactive (exist, not in App.jsx)

| File | Purpose | Classification |
|---|---|---|
| `api/advisor.js` | Rule-based advisor API client | **UI-Inactive** |
| `components/AdvisorButtons.jsx` | Advisor action buttons | **UI-Inactive** |
| `components/AdvisorSummaryPanel.jsx` | Advisor summary display | **UI-Inactive** |
| `components/RepoExplainerPanel.jsx` | Inline advisor explainer | **UI-Inactive** |
| `components/RoadmapPanel.jsx` | Roadmap steps display | **UI-Inactive** |
| `components/RepoCompareModal.jsx` | Repo comparison modal | **UI-Inactive** |
| `components/ProjectExplainerModal.jsx` | Standalone modal (logic is inside ProjectExplainButton) | **Deprecated** |

---

## Data / Index Files

| File | Purpose | Classification |
|---|---|---|
| `processed.json` | Primary NLP dataset | **Core** |
| `smart_profile_options.json` | Profile wizard options | **Core** |
| `vector_db/bm25_index.json` | BM25 index cache | **Core** (generated) |
| `vector_db/repo_embeddings.npy` | Embedding matrix | **Core** (generated) |
| `vector_db/repo_metadata.json` | Fingerprint metadata | **Core** (generated) |
| `search_index/*` | Old pickle index | **Deprecated** |
| `profile_options.json` | Old profile options | **Deprecated** |
| `repo_embeddings.npy` (root) | Stale copy | **Deprecated** |

---

## Docs

| File | Purpose |
|---|---|
| `docs/README.md` | Index for agents — start here |
| `docs/*.md` | Detailed reference docs |
