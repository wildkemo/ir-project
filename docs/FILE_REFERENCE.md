# RepoMind AI — File Reference

## Classification Key

- **Core** — Required for the system to function
- **Supporting** — Helper/utility; not directly critical but used by Core
- **Experimental** — Exists but not wired into the main flow
- **Deprecated** — Old version; superseded by a newer file
- **Unused** — Appears not to be imported by anything active

---

## Root-Level Scripts

| File | Purpose | Main Classes/Functions | Used By | Depends On | Classification |
|---|---|---|---|---|---|
| `scraper.py` | GitHub multi-topic HTML scraper + GitHub API repo fetcher | `FastGitHubScraper`, `run()`, `scrape_repo()`, `collect_repos()` | Manual execution | `requests`, `beautifulsoup4`, `python-dotenv` | **Core** |
| `process.py` | NLP processing pipeline: tokenization, normalization, scoring | `process_data()`, `clean_text()`, `compute_popularity_score()`, `compute_activity_score()`, `compute_quality_score()` | Manual execution | `nltk`, `json`, `re`, `math` | **Core** |
| `analysis.py` | Dataset statistics reporter | `run_analysis()`, `create_bar_chart()` | Manual execution | `processed.json`, `json`, `collections.Counter` | **Core** |
| `repo_utils.py` | Shared GitHub URL/repository validators and helpers | `is_github_repository()`, `resolve_full_name()`, `repository_docs()` | `backend/core/semantic_loader.py`, `backend/core/profile_loader.py`, `backend/api/repos.py` | `re` | **Core** |
| `smart_profile_recommender_v2.py` | Profile-based BM25 recommender + profile wizard options | `UserProfile`, `SmartProfileRecommender`, `DatasetOptionsBuilder`, `clean_query_terms()` | `backend/core/profile_loader.py`, `backend/core/semantic_loader.py` | `processed.json`, `json`, `math`, `re` | **Core** |
| `semantic_hybrid_recommender.py` | File-level alias: `SemanticHybridRecommender = GitHubRepoSearchEngine` | (alias only) | `backend/core/semantic_loader.py` | `core/search_engine.py` | **Core** (alias) |
| `quadrant_updater.py` | Upload processed.json to a Qdrant vector database | `sync_processed_json_to_qdrant()`, `build_document_text()`, `sanitize_payload()` | Manual execution (optional) | `qdrant-client`, `sentence-transformers`, `processed.json` | **Experimental** |
| `run_recommender_pipeline.py` | CLI runner for the profile recommender pipeline | N/A | Manual execution | `smart_profile_recommender_v2.py`, `processed.json` | **Supporting** |
| `run_search.py` | CLI search runner | N/A | Manual execution | `core/search_engine.py` | **Supporting** |
| `index_to_qdrant.py` | Thin wrapper for Qdrant indexing | N/A | Manual execution | `quadrant_updater.py` | **Supporting** |
| `requirements.txt` | Python package dependencies | N/A | `pip install -r requirements.txt` | N/A | **Core** |
| `.env.example` | Environment variable template | N/A | Developer reference | N/A | **Supporting** |

---

## `/backend/main.py`

| File | Purpose | Main Classes/Functions | Used By | Depends On | Classification |
|---|---|---|---|---|---|
| `backend/main.py` | FastAPI app factory: CORS, routers, health endpoint | `app`, `root()`, `health_check()` | `uvicorn` startup | All `backend/api/` routers | **Core** |

---

## `/backend/api/`

| File | Purpose | Main Classes/Functions | Used By | Depends On | Classification |
|---|---|---|---|---|---|
| `backend/api/search.py` | Search routes | `search_repositories()`, `explain_search_result()` | `backend/main.py` | `backend/core/semantic_loader.py`, `backend/schemas/search_schema.py` | **Core** |
| `backend/api/recommend.py` | Similar-repo recommendation routes | `recommend_similar_repositories()` | `backend/main.py` | `backend/core/semantic_loader.py`, `backend/schemas/search_schema.py` | **Core** |
| `backend/api/repos.py` | Repository listing/filter/detail routes | `list_repositories()`, `get_filter_options()`, `get_repository()` | `backend/main.py` | `backend/core/semantic_loader.py`, `backend/core/repo_sanitize.py`, `repo_utils.py` | **Core** |
| `backend/api/profile.py` | Profile wizard + recommendation routes | `get_profile_questions()`, `profile_recommend()`, `profile_search()` | `backend/main.py` | `backend/core/profile_loader.py`, `backend/schemas/profile_schema.py` | **Core** |
| `backend/api/advisor.py` | AI advisor routes (explain, roadmap, compare, summary) | `explain()`, `roadmap()`, `compare()`, `summary()` | `backend/main.py` | `backend/core/ai_advisor.py`, `backend/core/repo_explainer.py`, `backend/core/roadmap_generator.py`, `backend/core/repo_comparator.py` | **Core** |
| `backend/api/project_explainer.py` | Deep project explanation route | `explain_project_endpoint()` | `backend/main.py` | `backend/core/project_explainer.py` | **Core** |

---

## `/backend/core/`

| File | Purpose | Main Classes/Functions | Used By | Depends On | Classification |
|---|---|---|---|---|---|
| `backend/core/semantic_loader.py` | Singleton search engine loader + search/recommend adapters | `load_semantic_hybrid()`, `hybrid_search()`, `recommend_similar()`, `explain_result()`, `profile_from_payload()` | `backend/api/search.py`, `backend/api/recommend.py`, `backend/api/repos.py` | `core/search_engine.py` (via alias), `smart_profile_recommender_v2.py`, `repo_utils.py` | **Core** |
| `backend/core/profile_loader.py` | Profile recommender singleton + profile result normalization | `load_profile_recommender()`, `recommend_for_profile()`, `search_with_profile()`, `get_profile_questions_payload()` | `backend/api/profile.py` | `smart_profile_recommender_v2.py`, `repo_utils.py`, `processed.json`, `smart_profile_options.json` | **Core** |
| `backend/core/repo_intelligence.py` | Repository enrichment: tech stack, README sections, health/doc/contribution scores, intent detection | `enrich_repo()`, `extract_tech_stack()`, `extract_readme_sections()`, `compute_documentation_score()`, `compute_health_score()`, `compute_repo_intents()`, `detect_difficulty()` | `backend/core/ai_advisor.py`, `backend/core/repo_explainer.py`, `backend/core/roadmap_generator.py`, `backend/core/repo_comparator.py` | `re`, `math`, `datetime` | **Core** |
| `backend/core/repo_explainer.py` | Generates structured explanation for one repository | `explain_repo()`, `build_summary()`, `detect_strengths()`, `detect_weaknesses()`, `detect_best_for()`, `why_recommended()` | `backend/api/advisor.py`, `backend/core/ai_advisor.py`, `backend/core/repo_comparator.py` | `backend/core/repo_intelligence.py`, `backend/core/roadmap_generator.py` | **Core** |
| `backend/core/project_explainer.py` | Deep README analysis and full structured project explanation | `explain_project()`, `normalize_repo()`, `extract_readme_sections()`, `extract_section_snippets()`, `extract_tech_stack()`, `build_strengths()`, `build_limitations()`, `build_how_to_use()` | `backend/api/project_explainer.py` | `re`, `datetime` | **Core** |
| `backend/core/roadmap_generator.py` | Goal-aware roadmap generation (learning/contribution/production/portfolio) | `generate_roadmap()`, `generate_learning_roadmap()`, `generate_contribution_roadmap()`, `generate_production_roadmap()`, `generate_portfolio_roadmap()` | `backend/api/advisor.py`, `backend/core/ai_advisor.py`, `backend/core/repo_explainer.py` | `backend/core/repo_intelligence.py` | **Core** |
| `backend/core/ai_advisor.py` | Multi-repo advisory: selects best repo, generates summary, builds advisor score | `advise()`, `build_summary()`, `_advisor_score()`, `_pick_best_by()` | `backend/api/advisor.py` | `backend/core/repo_intelligence.py`, `backend/core/repo_explainer.py`, `backend/core/roadmap_generator.py` | **Core** |
| `backend/core/repo_comparator.py` | Side-by-side repository comparison | `compare_repos()`, `_score_for_goal()` | `backend/api/advisor.py` | `backend/core/repo_intelligence.py`, `backend/core/repo_explainer.py` | **Core** |
| `backend/core/http_errors.py` | FastAPI error helpers | `raise_not_found()`, `raise_server_error()` | All `backend/api/` modules | `fastapi.HTTPException` | **Supporting** |
| `backend/core/repo_sanitize.py` | Returns public-safe repo summary fields | `public_repo_summary()` | `backend/api/repos.py` | N/A | **Supporting** |
| `backend/core/engine_loader.py` | Thin engine loader wrapper | N/A | (minimal usage) | `backend/core/semantic_loader.py` | **Supporting** |

---

## `/backend/schemas/`

| File | Purpose | Main Classes/Functions | Used By | Depends On | Classification |
|---|---|---|---|---|---|
| `backend/schemas/search_schema.py` | Pydantic models for search/recommend/explain requests | `SearchRequest`, `RecommendRequest`, `ExplainRequest`, `ProfileContext` | `backend/api/search.py`, `backend/api/recommend.py` | `pydantic` | **Core** |
| `backend/schemas/advisor.py` | Pydantic models for advisor requests | `ExplainRepoRequest`, `RoadmapRequest`, `CompareReposRequest`, `AdvisorSummaryRequest` | `backend/api/advisor.py` | `pydantic`, `backend/schemas/validators.py` | **Core** |
| `backend/schemas/profile_schema.py` | Pydantic models for profile requests | `ProfileRecommendRequest`, `ProfileSearchRequest` | `backend/api/profile.py` | `pydantic` | **Core** |
| `backend/schemas/project_explainer.py` | Pydantic model for project explainer | `ProjectExplainRequest` | `backend/api/project_explainer.py` | `pydantic` | **Core** |
| `backend/schemas/validators.py` | Shared validator functions | `validate_repo_payload()`, `validate_results_list()`, `MAX_QUERY_CHARS`, `MAX_RESULTS_ITEMS` | `backend/schemas/advisor.py` | `pydantic` | **Supporting** |

---

## `/core/` (Standalone/Legacy)

| File | Purpose | Classification |
|---|---|---|
| `core/search_engine.py` | **PRIMARY** — `GitHubRepoSearchEngine` + `BM25Index` + CLI | **Core** |
| `core/repo_intelligence.py` | Duplicate of `backend/core/repo_intelligence.py` | **Deprecated** |
| `core/repo_explainer.py` | Duplicate of `backend/core/repo_explainer.py` | **Deprecated** |
| `core/project_explainer.py` | Duplicate of `backend/core/project_explainer.py` | **Deprecated** |
| `core/roadmap_generator.py` | Duplicate of `backend/core/roadmap_generator.py` | **Deprecated** |
| `core/repo_comparator.py` | Duplicate of `backend/core/repo_comparator.py` | **Deprecated** |
| `core/profile_loader.py` | Duplicate of `backend/core/profile_loader.py` | **Deprecated** |
| `core/semantic_loader.py` | Duplicate of `backend/core/semantic_loader.py` | **Deprecated** |
| `core/repo_utils.py` | Duplicate of root `repo_utils.py` | **Deprecated** |
| `core/http_errors.py` | Duplicate of `backend/core/http_errors.py` | **Deprecated** |
| `core/repo_sanitize.py` | Duplicate of `backend/core/repo_sanitize.py` | **Deprecated** |
| `core/engine_loader.py` | Thin loader | **Supporting** |
| `core/profile_engine.py` | Large profile engine (~27 KB) — possibly older version of `smart_profile_recommender_v2.py` | **Deprecated/Unused** |
| `core/rag_advisor.py` | RAG advisor stub | **Experimental** |
| `core/hybrid_ranker.py` | Empty stub (57 bytes) | **Unused** |
| `core/recommender.py` | Empty stub (57 bytes) | **Unused** |

---

## `/api/` (Old API Layer)

| File | Purpose | Classification |
|---|---|---|
| `api/search.py` | Old search routes | **Deprecated** |
| `api/recommend.py` | Old recommend routes | **Deprecated** |
| `api/explain.py` | Old explain routes | **Deprecated** |
| `api/schemas/` | Old schema definitions | **Deprecated** |

---

## `/frontend/src/`

| File | Purpose | Main Functions | Used By | Classification |
|---|---|---|---|---|
| `src/main.jsx` | React app entry point | N/A | Browser | **Core** |
| `src/App.jsx` | Root component — all state, all views, routing logic | All state hooks, view switching | `main.jsx` | **Core** |
| `src/App.css` | Main component styles | N/A | `App.jsx` | **Core** |
| `src/index.css` | Global CSS reset + design tokens | N/A | `main.jsx` | **Core** |
| `src/api/client.js` | Axios instance + all API call functions | `searchRepos()`, `recommendRepos()`, `explainRepo()`, `generateRoadmap()`, `compareRepos()`, `advisorSummary()`, `explainProject()`, `getProfileQuestions()`, `recommendFromProfile()` | All components | **Core** |
| `src/api/advisor.js` | Re-export for advisor calls | N/A | `App.jsx` | **Supporting** |
| `src/api/projectExplainer.js` | Re-export for project explainer | N/A | Components | **Supporting** |
| `src/components/SearchBar.jsx` | Search input component | N/A | `App.jsx` | **Core** |
| `src/components/Filters.jsx` | Filter panel (language, license, topic, min_stars) | N/A | `App.jsx` | **Core** |
| `src/components/RepoCard.jsx` | Individual result card with all action buttons | N/A | `App.jsx` | **Core** |
| `src/components/ProfileWizard.jsx` | Multi-step profile questionnaire | N/A | `App.jsx` | **Core** |
| `src/components/ProfileRepoCard.jsx` | Card for profile recommendation results | N/A | `App.jsx` | **Core** |
| `src/components/RecommendationPanel.jsx` | Similar repos side panel | N/A | `App.jsx` | **Core** |
| `src/components/RepoExplainerPanel.jsx` | Inline advisor explanation panel | N/A | `App.jsx` | **Core** |
| `src/components/ProjectExplainButton.jsx` | "Explain Project" button + logic | N/A | `RepoCard.jsx`, `App.jsx` | **Core** |
| `src/components/ProjectExplainerModal.jsx` | Full project explanation modal display | N/A | `App.jsx` | **Core** |
| `src/components/AdvisorSummaryPanel.jsx` | AI advisor summary display | N/A | `App.jsx` | **Core** |
| `src/components/AdvisorButtons.jsx` | Advisor action buttons row | N/A | `App.jsx` | **Core** |
| `src/components/RoadmapPanel.jsx` | Roadmap steps display | N/A | `App.jsx` | **Core** |
| `src/components/RepoCompareModal.jsx` | Repo comparison modal | N/A | `App.jsx` | **Core** |
| `src/components/ScoreBreakdown.jsx` | Score breakdown display (BM25/semantic/profile) | N/A | `RepoCard.jsx` | **Supporting** |
| `src/components/EmptyState.jsx` | Empty results display | N/A | `App.jsx` | **Supporting** |
| `src/components/LoadingState.jsx` | Loading indicator | N/A | `App.jsx` | **Supporting** |
| `src/components/ThemeToggle.jsx` | Dark/light mode toggle button | N/A | `App.jsx` | **Supporting** |
| `src/hooks/useTheme.js` | Dark/light theme persistence (localStorage) | `useTheme()` | `App.jsx` | **Supporting** |
| `src/utils/format.js` | Number/date formatting | `formatNumber()`, `formatDate()` | Components | **Supporting** |
| `src/utils/profileStorage.js` | LocalStorage profile persistence | `saveProfile()`, `loadProfile()` | `App.jsx` | **Supporting** |
| `src/utils/repoDisplay.js` | Language color mapping, display helpers | `getLanguageColor()` | Components | **Supporting** |
