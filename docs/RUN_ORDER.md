# RepoMind AI — Run Order (Beginner Guide)

Step-by-step setup from a fresh clone.

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git
- (Optional) [Ollama](https://ollama.com) for AI explain/roadmap features

---

## Step 1 — Clone and Enter the Project

```bash
git clone <repository-url>
cd ir-project
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

There is no `requirements.txt` in the repo. Install manually:

```bash
pip install fastapi "uvicorn[standard]" pydantic numpy sentence-transformers \
  nltk requests beautifulsoup4 python-dotenv qdrant-client
```

NLTK data downloads automatically on first `process.py` run.

---

## Step 4 — Configure Environment Variables

Create `.env` at project root:

```env
# Optional — for re-scraping (raises GitHub rate limit)
GITHUB_TOKEN=your_token_here

# Optional — for Ollama RAG features
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b
```

> If you only run search with existing `processed.json`, you can skip all env vars.

---

## Step 5 — [OPTIONAL] Re-Scrape GitHub Data

Skip if `processed.json` already exists (it is included in the repository).

```bash
python scraper.py
```

- Output: `new_data.json`
- Takes 5–30 minutes depending on token availability
- Without token: 60 GitHub API requests/hour

---

## Step 6 — [OPTIONAL] Process Raw Data

Skip if `processed.json` already exists.

```bash
python process.py
```

- Reads `new_data.json` → writes `processed.json`
- Takes 30 seconds to 3 minutes

---

## Step 7 — [OPTIONAL] Dataset Analysis

```bash
python analysis.py
```

Prints vocabulary stats, top languages, top repos. No files generated.

---

## Step 8 — Start the FastAPI Backend

**Must run from project root** (required for root-level imports):

```bash
uvicorn backend.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

> First search request takes 1–5 minutes while the index builds in `vector_db/`.

---

## Step 9 — Install Frontend Dependencies

New terminal:

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

- UI: http://localhost:5173
- Vite proxies `/api` requests to the backend

---

## Step 11 — [OPTIONAL] Start Ollama for AI Features

New terminal:

```bash
ollama serve
ollama pull qwen2.5:1.5b
```

Without Ollama, "Explain with AI" and "AI Roadmap" buttons will show errors. All other features work.

---

## Step 12 — Verify the System

1. Open http://localhost:5173
2. Complete the profile wizard (or skip if stored profile exists)
3. See profile recommendations
4. Search for e.g. "machine learning python"
5. On a result card, try:
   - **Explain Project** — instant rule-based analysis
   - **Explain with AI** — Ollama explanation (needs Ollama)
   - **Similar Projects** — embedding neighbors
6. Check backend health indicator (green "Live" pill in top bar)

---

## [OPTIONAL] Step 13 — Qdrant Upload

```bash
docker run -p 6333:6333 qdrant/qdrant
python quadrant_updater.py
```

Main search engine does not use Qdrant.

---

## [OPTIONAL] Step 14 — PostgreSQL (docker-compose)

```bash
docker compose up -d
```

Starts Postgres on host port `5433`. Not connected to app code yet.

---

## Common Issues

| Issue | Solution |
|---|---|
| `FileNotFoundError: processed.json` | Run `python process.py` or ensure file exists |
| First search very slow | Normal — index building. Wait 1–5 min. |
| `Cannot reach API` | Start uvicorn from project root |
| `ModuleNotFoundError: repo_utils` | Run uvicorn from project root, not `cd backend` |
| GitHub rate limit | Add `GITHUB_TOKEN` to `.env` |
| RAG buttons fail | Start Ollama: `ollama serve` + `ollama pull qwen2.5:1.5b` |
| CORS errors | Ensure frontend is on `:5173` (hardcoded in main.py) |
| No search results | Confirm backend running and `processed.json` exists |

---

## Full Execution Order Summary

```bash
# Run once (data pipeline):
python scraper.py          # → new_data.json
python process.py          # → processed.json
python analysis.py         # → console report (optional)

# Run every session:
uvicorn backend.main:app --reload --port 8000   # Terminal 1 (project root)
cd frontend && npm run dev                         # Terminal 2
ollama serve                                       # Terminal 3 (optional, for RAG)

# Optional:
python quadrant_updater.py   # Qdrant upload
docker compose up -d         # PostgreSQL
```
