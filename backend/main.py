"""Application entry point — extends existing API with user management."""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import OperationalError
from backend.core.rate_limit import limiter
from sqlalchemy import text

from backend.api.admin import router as admin_router
from backend.api.advisor import router as advisor_router
from backend.api.auth import router as auth_router
from backend.api.favorites import router as favorites_router
from backend.api.history import router as history_router
from backend.api.preferences import router as preferences_router
from backend.api.profile import router as profile_router
from backend.api.project_explainer import router as project_explainer_router
from backend.api.rag import router as rag_router
from backend.api.recommend import router as recommend_router
from backend.api.repos import router as repos_router
from backend.api.search import router as search_router
from backend.api.users import router as users_router
from backend.core.logging_config import setup_logging
from backend.database.session import engine

load_dotenv()
setup_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def _parse_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify database connectivity on startup."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection established")
    except Exception as exc:
        logger.warning("PostgreSQL not available at startup: %s", exc)
    yield


app = FastAPI(
    title="Open-Source Project Search Engine API",
    description="Hybrid BM25 + semantic search backend with user management.",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(OperationalError)
async def database_unavailable_handler(_request: Request, exc: OperationalError):
    """Return a clear message when PostgreSQL is not reachable."""
    logger.error("Database unavailable: %s", exc.orig if exc.orig else exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "Database is unavailable. Start PostgreSQL with "
                "'docker compose up -d postgres', then run 'alembic upgrade head'."
            )
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured request logging without sensitive data."""
    response = await call_next(request)
    if request.url.path not in ("/health", "/"):
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
            },
        )
    return response


@app.get("/")
def root():
    return {
        "message": "Open-Source Project Search Engine API",
        "docs": "/docs",
        "health": "/health",
        "auth": "/auth",
    }


@app.get("/health")
def health_check():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    return {
        "status": "ok",
        "database": db_status,
    }


# Existing routers (unchanged paths)
app.include_router(search_router)
app.include_router(recommend_router)
app.include_router(repos_router)
app.include_router(profile_router)
app.include_router(advisor_router)
app.include_router(project_explainer_router)
app.include_router(rag_router)

# User management routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(preferences_router)
app.include_router(favorites_router)
app.include_router(history_router)
app.include_router(admin_router)
