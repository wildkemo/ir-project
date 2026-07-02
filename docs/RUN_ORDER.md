# RepoMind AI — Run Order (Beginner Guide)

This guide explains exactly how to set up and run the project from scratch.

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git

---

## Step 1 — Clone and Enter the Project

```bash
git clone <repository-url>
cd "RepoMind AI"
```

---

## Step 2 — Create Python Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

---

## Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi`, `uvicorn`, `pydantic` — API server
- `numpy`, `nltk`, `requests`, `beautifulsoup4`, `python-dotenv` — data pipeline
- `sentence-transformers` — semantic search embeddings
- `qdrant-client` — optional vector database

The first run will also download NLTK data automatically (stopwords, wordnet).

---

## Step 4 — Configure Environment Variables

Copy the example file and edit if needed:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Enable /docs and /redoc endpoints (development)
DEBUG=true

# (Optional) GitHub token raises API rate limit from 60 to 5000 req/hour
# Required if you plan to re-scrape data
GITHUB_TOKEN=your_token_here

# (Optional) Override allowed frontend origins
# CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> **If you only want to run the backend with existing data, you can skip the token.**

---

## Step 5 — [OPTIONAL] Re-Scrape GitHub Data

> **Skip this step** if `processed.json` already exists (it is included in the repository).

```bash
python scraper.py
```

- This crawls GitHub topics and collects repository data.
- Output: `new_data.json` (~50–2000 repositories)
- Takes 5–30 minutes depending on token availability.
- Without a token, GitHub will rate-limit you to 60 requests/hour.

---

## Step 6 — [OPTIONAL] Process the Raw Data

> **Skip this step** if `processed.json` already exists.

```bash
python process.py
```

- Reads `new_data.json`, applies NLP processing, computes scores.
- Output: `processed.json`
- Takes 30 seconds to 3 minutes.

---

## Step 7 — [OPTIONAL] Run Dataset Analysis

> Optional — for understanding the dataset.

```bash
python analysis.py
```

- Prints a terminal report: vocabulary size, top terms, top languages, top repos by stars.
- No files are generated.

---

## Step 8 — Start the FastAPI Backend

```bash
 python -m uvicorn 8000backend.main:app --reload --port ```

The server starts at: **http://127.0.0.1:8000**

API documentation (when `DEBUG=true`):
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

> **First search request will take 1–5 minutes** as the search index is built automatically.
> Subsequent requests use the cached index in `storage/`.

---

## Step 9 — Install Frontend Dependencies

In a new terminal:

```bash
cd frontend
npm install
```

---

## Step 10 — Start the React Frontend

```bash
cd frontend
npm run dev
```

The frontend starts at: **http://localhost:5173**

The Vite dev server automatically proxies all `/api` requests to `http://127.0.0.1:8000`.

---

## Step 11 — Verify the System

1. Open http://localhost:5173
2. Type a search query (e.g., "machine learning python")
3. Results should appear within a few seconds (after the first-time index build)
4. Try the Profile Wizard button to get personalized recommendations
5. Click any repo card to see the "Explain Project" button

---

## [OPTIONAL] Step 12 — Upload to Qdrant (Advanced)

> Only needed if you want to use Qdrant as your vector database.

First, start Qdrant:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Then upload:

```bash
python quadrant_updater.py
```

Configure via environment variables:

```env
QDRANT_URL=http://127.0.0.1:6333
QDRANT_COLLECTION=github_repos
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_SIZE=384
```

> **Note:** The main search engine does NOT use Qdrant. This is for future integration.

---

## Common Issues

| Issue | Solution |
|---|---|
| `FileNotFoundError: processed.json` | Run `python process.py` first |
| First search is very slow (1–5 min) | Normal — the search index is being built. Wait for it. |
| `Cannot reach API at http://127.0.0.1:8000` | Make sure `uvicorn` is running |
| Rate limit from GitHub | Add `GITHUB_TOKEN` to `.env` |
| `ModuleNotFoundError: sentence_transformers` | Run `pip install sentence-transformers` |
| CORS errors in browser | Ensure `DEBUG=true` in `.env` and frontend is on `:5173` |
| Frontend shows no results | Confirm the backend is running and `processed.json` exists |

---

## Full Execution Order Summary

```
# Run once (data pipeline):
python scraper.py          # → new_data.json
python process.py          # → processed.json
python analysis.py         # → console report (optional)

# Run every time (server):
uvicorn backend.main:app --reload --port 8000   # Terminal 1
cd frontend && npm run dev                       # Terminal 2

# Optional:
python quadrant_updater.py  # Only if using Qdrant
```
