# RepoMind AI — Project Overview

## Purpose

**RepoMind AI** (internally called *OpenSeek*) is a **Web Intelligence Data Pipeline and Personalized GitHub Repository Discovery Engine** built for the **CS313x – Information Retrieval & Data Analysis** course.

The project collects open-source GitHub repository data, processes it using NLP techniques, indexes it for search, and serves it through a modern web application that allows users to:

- **Search** repositories using a hybrid BM25 + semantic (embedding-based) engine
- **Discover** repositories matched to their personal developer profile
- **Understand** repositories without leaving the app (automated explanations, scores, tech stack detection)
- **Compare** two repositories side-by-side
- **Generate** personalized roadmaps for any repository based on user goals
- **Get AI Advisor summaries** on a set of search results

---

## Main Features

| Feature | Description |
|---|---|
| Hybrid Search | BM25 (lexical) + Sentence-Transformer (semantic) + popularity scoring |
| Profile-based Recommendation | Multi-dimensional user profile questionnaire + BM25 re-ranking |
| Repo Explainer | Auto-generates summary, strengths, weaknesses, difficulty, tech stack |
| Roadmap Generator | Goal-aware (learning / contribution / production / portfolio) step-by-step plans |
| Repo Comparator | Side-by-side scored comparison of two repositories |
| AI Advisor | Template-based multi-repo advisory summary; selects best repo per goal |
| Project Explainer | Deep README analysis, section detection, snippet extraction |
| Score Breakdown | Every result shows bm25, semantic, profile/popularity component scores |

---

## Technology Stack

### Backend
| Component | Technology |
|---|---|
| Web Framework | FastAPI 0.115+ |
| ASGI Server | Uvicorn |
| Data Validation | Pydantic v2 |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| BM25 Engine | Custom pure-Python implementation (`core/search_engine.py`) |
| Vector Storage | NumPy `.npy` files (local) + optional Qdrant |
| NLP Preprocessing | NLTK (stopwords, WordNet lemmatization) |
| HTTP Requests | Requests + BeautifulSoup4 |
| Environment | python-dotenv |

### Frontend
| Component | Technology |
|---|---|
| Framework | React 19 |
| Build Tool | Vite 8 |
| HTTP Client | Axios |
| Icons | Lucide React |
| Styling | Vanilla CSS |
| Dev Proxy | Vite proxy → `http://127.0.0.1:8000` |

### Optional / Infrastructure
| Component | Technology |
|---|---|
| Vector DB | Qdrant (optional, via `quadrant_updater.py`) |
| LLM / RAG | NOT currently used; all AI is template/rule-based |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      DATA PIPELINE                       │
│  scraper.py → new_data.json → process.py → processed.json│
│                     analysis.py                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                         │
│  backend/main.py                                          │
│  ├── /search        (Hybrid BM25 + Semantic)              │
│  ├── /recommend     (Similar Repos by Embedding)          │
│  ├── /repos         (List / Filter / Details)             │
│  ├── /profile       (Profile Wizard + Recommendation)     │
│  ├── /api/advisor   (Explain, Roadmap, Compare, Summary)  │
│  └── /api/project-explainer (Deep README Analysis)        │
└─────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────┐
│               FRONTEND (React + Vite)                    │
│  Search Bar → Results Cards → Repo Explainer Panel       │
│  Profile Wizard → Profile Recommendations                 │
│  AI Advisor Summary → Roadmap Panel → Compare Modal       │
└─────────────────────────────────────────────────────────┘
```

---

## Main Modules

| Module | Location | Role |
|---|---|---|
| Data Scraper | `scraper.py` | GitHub topic crawling + GitHub API repo extraction |
| Data Processor | `process.py` | NLP tokenization, normalization, scoring |
| Data Analyzer | `analysis.py` | Dataset statistics and corpus exploration |
| Search Engine | `core/search_engine.py` | BM25 + Semantic hybrid, index builder, CLI |
| Profile Recommender | `smart_profile_recommender_v2.py` | Profile matching + personalized BM25 search |
| Semantic Loader | `backend/core/semantic_loader.py` | Singleton engine loader + search adapter |
| Profile Loader | `backend/core/profile_loader.py` | Profile recommender adapter for FastAPI |
| Repo Intelligence | `backend/core/repo_intelligence.py` | Feature enrichment (tech stack, README sections, health scores) |
| Repo Explainer | `backend/core/repo_explainer.py` | Explanation generation per repo |
| Project Explainer | `backend/core/project_explainer.py` | Deep README analysis + structured explanation |
| Roadmap Generator | `backend/core/roadmap_generator.py` | Goal-based roadmap generation |
| Repo Comparator | `backend/core/repo_comparator.py` | Side-by-side comparison |
| AI Advisor | `backend/core/ai_advisor.py` | Multi-repo advisory summary |

---

## Overall Execution Flow

```
1. [ONCE] python scraper.py        → new_data.json   (raw scraped repos)
2. [ONCE] python process.py        → processed.json  (NLP-processed + scored)
3. [ONCE] python analysis.py       → console output  (dataset stats)
4. [SERVER] uvicorn backend.main:app  → FastAPI starts, auto-builds indexes on first request
5. [FRONTEND] npm run dev (in /frontend)  → React dev server on :5173
```

The search index (BM25 + embeddings) is **lazily built on first API request** and cached in `storage/` (or `vector_db/`). Subsequent requests use cached indexes.
