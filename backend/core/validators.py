"""Input validation and sanitization helpers."""

import re

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,50}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
REPO_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z0-9._\-]+/[a-zA-Z0-9._\-]+$")


def sanitize_username(value: str) -> str:
    """Normalize and validate a username."""
    cleaned = value.strip()
    if not USERNAME_PATTERN.match(cleaned):
        raise ValueError(
            "Username must be 3-50 characters and contain only letters, numbers, and underscores"
        )
    return cleaned


def sanitize_email(value: str) -> str:
    """Normalize and validate an email address."""
    cleaned = value.strip().lower()
    if not EMAIL_PATTERN.match(cleaned):
        raise ValueError("Invalid email address")
    return cleaned


def sanitize_repo_identifier(value: str) -> str:
    """Normalize and validate an owner/repo identifier."""
    cleaned = value.strip()
    if cleaned.startswith("https://github.com/"):
        cleaned = cleaned.replace("https://github.com/", "").rstrip("/")
    if not REPO_IDENTIFIER_PATTERN.match(cleaned):
        raise ValueError("Repository identifier must be in owner/repo format")
    return cleaned


def sanitize_search_query(value: str) -> str:
    """Sanitize a search query string."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Search query cannot be empty")
    if len(cleaned) > 500:
        raise ValueError("Search query is too long (max 500 characters)")
    return cleaned
