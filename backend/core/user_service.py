"""User profile and preference services."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from backend.models.preferred_framework import PreferredFramework
from backend.models.preferred_language import PreferredLanguage
from backend.models.preferred_topic import PreferredTopic
from backend.models.user import User
from backend.models.user_preference import UserPreference
from backend.schemas.preferences_schema import UserPreferencesRequest, UserPreferencesResponse
from backend.schemas.user_schema import UserUpdateRequest


def update_user_profile(db: Session, user: User, payload: UserUpdateRequest) -> User:
    """Update user profile fields."""
    if payload.username and payload.username != user.username:
        existing = db.query(User).filter(User.username == payload.username).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        user.username = payload.username

    if payload.avatar is not None:
        user.avatar = payload.avatar
    if payload.bio is not None:
        user.bio = payload.bio

    db.commit()
    db.refresh(user)
    return user


def _ensure_preferences(db: Session, user: User) -> UserPreference:
    if user.preferences is None:
        prefs = UserPreference(user_id=user.id)
        db.add(prefs)
        db.flush()
        user.preferences = prefs
    return user.preferences


def get_user_preferences(db: Session, user: User) -> UserPreferencesResponse:
    """Return user preferences as a response schema."""
    user = (
        db.query(User)
        .options(
            joinedload(User.preferences),
            joinedload(User.preferred_languages),
            joinedload(User.preferred_topics),
            joinedload(User.preferred_frameworks),
        )
        .filter(User.id == user.id)
        .first()
    )
    prefs = user.preferences if user else None
    return UserPreferencesResponse(
        experience_level=prefs.experience_level if prefs else None,
        preferred_license=prefs.preferred_license if prefs else None,
        project_type=prefs.project_type if prefs else None,
        goal=prefs.goal if prefs else None,
        repo_kind=prefs.repo_kind if prefs else None,
        complexity=prefs.complexity if prefs else None,
        languages=[item.language for item in (user.preferred_languages if user else [])],
        topics=[item.topic for item in (user.preferred_topics if user else [])],
        frameworks=[item.framework for item in (user.preferred_frameworks if user else [])],
    )


def update_user_preferences(
    db: Session, user: User, payload: UserPreferencesRequest
) -> UserPreferencesResponse:
    """Update user preferences and related lists."""
    user = (
        db.query(User)
        .options(
            joinedload(User.preferences),
            joinedload(User.preferred_languages),
            joinedload(User.preferred_topics),
            joinedload(User.preferred_frameworks),
        )
        .filter(User.id == user.id)
        .first()
    )
    prefs = _ensure_preferences(db, user)

    prefs.experience_level = payload.experience_level
    prefs.preferred_license = payload.preferred_license
    prefs.project_type = payload.project_type
    prefs.goal = payload.goal
    prefs.repo_kind = payload.repo_kind
    prefs.complexity = payload.complexity

    user.preferred_languages.clear()
    for lang in payload.languages:
        cleaned = lang.strip()
        if cleaned:
            user.preferred_languages.append(PreferredLanguage(language=cleaned))

    user.preferred_topics.clear()
    for topic in payload.topics:
        cleaned = topic.strip()
        if cleaned:
            user.preferred_topics.append(PreferredTopic(topic=cleaned))

    user.preferred_frameworks.clear()
    for framework in payload.frameworks:
        cleaned = framework.strip()
        if cleaned:
            user.preferred_frameworks.append(PreferredFramework(framework=cleaned))

    db.commit()
    return get_user_preferences(db, user)


def preferences_to_profile_dict(db: Session, user: User) -> dict | None:
    """Convert stored preferences to profile dict for recommendation engine."""
    prefs_response = get_user_preferences(db, user)
    if not any(
        [
            prefs_response.experience_level,
            prefs_response.project_type,
            prefs_response.goal,
            prefs_response.repo_kind,
            prefs_response.complexity,
            prefs_response.languages,
        ]
    ):
        return None

    profile = {
        "project_type": prefs_response.project_type,
        "goal": prefs_response.goal,
        "level": prefs_response.experience_level,
        "repo_kind": prefs_response.repo_kind,
        "complexity": prefs_response.complexity,
    }
    if prefs_response.languages:
        profile["language"] = prefs_response.languages[0]
    return {k: v for k, v in profile.items() if v is not None}
