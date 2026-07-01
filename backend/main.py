from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.search import router as search_router
from backend.api.recommend import router as recommend_router
from backend.api.repos import router as repos_router
from backend.api.profile import router as profile_router
from backend.api.advisor import router as advisor_router
from backend.api.project_explainer import router as project_explainer_router
from backend.api.rag import router as rag_router

app = FastAPI(
    title="Open-Source Project Search Engine API",
    description="Hybrid BM25 + semantic search backend for GitHub repository discovery.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Open-Source Project Search Engine API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(repos_router)
app.include_router(profile_router)
app.include_router(advisor_router)
app.include_router(project_explainer_router)
app.include_router(rag_router)