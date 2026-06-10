# 🧠 Project A-Z: Open-Source Discovery & Search Engine

This document provides a comprehensive overview of the project, detailing the architecture, the purpose of each file, and how the entire pipeline fits together.

---

## 🚀 1. Project Mission
This project is an advanced **Information Retrieval (IR)** and **Semantic Search** platform designed to help developers discover open-source GitHub repositories. It goes beyond simple keyword matching by combining traditional **BM25 ranking** with **Vector Embeddings (Semantic Search)** and **Personalized User Profiling**.

---

## 🏗️ 2. High-Level Architecture
The system follows a modular data pipeline architecture:
1.  **Collection:** Scrapes GitHub for repository data.
2.  **Processing:** Cleans, tokenizes, and normalizes text for IR.
3.  **Indexing:** Stores data in a Vector Database (Qdrant) and creates a BM25 index.
4.  **Backend (API):** A FastAPI server that handles search, recommendations, and profile management.
5.  **Frontend (UI):** A React-based web dashboard for user interaction.

---

## 📂 3. File-by-File Guide

### 🛠️ Root Directory: The Core Pipeline
| File | Purpose |
| :--- | :--- |
| `scraper.py` | **Data Collection:** Crawls GitHub repository pages, respects `robots.txt`, and saves raw data to `data.json`. |
| `process.py` | **NLP Processing:** Tokenizes text, removes stopwords, and performs stemming/lemmatization to produce `processed.json`. |
| `analysis.py` | **Data Understanding:** Generates statistics about the dataset (keyword frequency, vocabulary size, trends). |
| `semantic_hybrid_recommender.py` | **Search Engine Logic:** The "brain" of the project. Implements the Hybrid Search (BM25 + Semantic) and ranking algorithms. |
| `smart_profile_recommender_v2.py` | **Personalization:** Handles user profiling and calculates document-profile alignment scores. |
| `quadrant_updater.py` | **Vector DB Sync:** Generates embeddings (using Sentence-Transformers) and uploads them to the Qdrant database. |
| `index_to_qdrant.py` | A wrapper script for `quadrant_updater.py` for backward compatibility. |
| `run_search.py` | CLI tool to test search queries directly from the terminal. |
| `run_recommender_pipeline.py` | CLI tool to test the recommendation engine. |
| `repo_utils.py` | Shared utility functions for repository data handling. |

### 🌐 Backend (`/backend`)
The backend is built with **FastAPI** and serves as the bridge between the search engine and the frontend.

| Path | Purpose |
| :--- | :--- |
| `main.py` | The entry point for the FastAPI application. Sets up CORS and includes routers. |
| `api/search.py` | Handles `/api/search` requests (Hybrid search logic). |
| `api/recommend.py` | Handles `/api/recommend` requests for personalized repo suggestions. |
| `api/repos.py` | Provides metadata and details for individual repositories. |
| `api/profile.py` | Manages user profile creation and storage. |
| `core/engine_loader.py` | Dynamically loads and caches the Search Engine and BM25 index. |
| `core/semantic_loader.py` | Manages the Qdrant client connection and embedding models. |

### 🎨 Frontend (`/frontend`)
The frontend is a modern **React** application built with **Vite**.

| Path | Purpose |
| :--- | :--- |
| `src/App.jsx` | Main application component and layout. |
| `src/components/SearchBar.jsx` | The search interface with real-time feedback. |
| `src/components/RepoCard.jsx` | Displays individual repository information (stars, forks, description). |
| `src/components/ProfileWizard.jsx` | An interactive multi-step form to build the user's technical profile. |
| `src/components/RecommendationPanel.jsx` | Displays personalized repo suggestions based on the user's profile. |
| `src/api/client.js` | Axios configuration for communicating with the FastAPI backend. |

### 📚 Documentation
| File | Purpose |
| :--- | :--- |
| `README.md` | Standard project entry point and high-level description. |
| `GEMINI.md` | Core project overview and building/running instructions for the agent. |
| `EXCUTION.md` | Step-by-step sequential execution guide for the pipeline. |
| `Pipeline.md` | Detailed technical specification of the data collection and processing layers. |
| `app_arch.md` | Philosophical and architectural design document. |
| `COURSE-REQUIREMENTS.md` | Official course checklist (CS313x) and how they are met. |
| `SCRAPER_DOCUMENTATION.md` | Deep dive into the scraping logic and GitHub-specific parsing. |

### ⚙️ Configuration & Metadata
| File | Purpose |
| :--- | :--- |
| `profile_options.json` | Defines the available options for the user profiling wizard. |
| `smart_profile_options.json` | Advanced weighting and mapping for the personalization engine. |
| `cache.json` | Stores temporary data (like scraped URLs) to avoid redundant requests. |
| `robots.txt` | Standard web crawler instructions for the scraper. |

### 🗄️ Data & Storage
| Path | Purpose |
| :--- | :--- |
| `data.json` | Raw scraped repository data. |
| `processed.json` | Cleaned and tokenized data ready for indexing. |
| `search_index/` | Contains the serialized BM25 index and document mappings. |
| `qdrant_storage/` | Local storage for the Qdrant vector database (if running locally). |
| `repo_embeddings.npy` | Pre-calculated vector embeddings for the repositories. |

---

## 🔄 4. The Data Flow (Step-by-Step)

1.  **Ingestion:** `scraper.py` runs and populates `data.json`.
2.  **Refining:** `process.py` cleans the text and creates `processed.json`.
3.  **Indexing:** `quadrant_updater.py` converts descriptions into 384-dimensional vectors and stores them in Qdrant.
4.  **Querying:**
    - User types "machine learning" in the Frontend.
    - Backend receives query and passes it to `semantic_hybrid_recommender.py`.
    - **BM25** finds exact keyword matches.
    - **Semantic Search** finds repos related to "AI/Neural Networks" even if those exact words weren't in the query.
    - The results are **Ranked** using a hybrid score and returned to the user.

---

## ✨ 5. Core AI Features
- **Semantic Understanding:** Uses `all-MiniLM-L6-v2` transformer model to understand the *meaning* of repo descriptions.
- **Explainable AI:** The system provides reasoning for its recommendations (e.g., *"Matches your preference for Python and Data Science"*).
- **Personalization:** A weighted scoring model that aligns repo metadata with a dynamic user profile.
