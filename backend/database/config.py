"""Database configuration loaded from environment variables."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Build PostgreSQL connection URL from environment."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    user = os.getenv("POSTGRES_USER", "repomind")
    password = os.getenv("POSTGRES_PASSWORD", "repomind123")
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5433")
    db = os.getenv("POSTGRES_DB", "repomind")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


@lru_cache
def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not set in environment")
    return secret


@lru_cache
def get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


@lru_cache
def get_access_token_expire_minutes() -> int:
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


@lru_cache
def get_refresh_token_expire_days() -> int:
    return int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
