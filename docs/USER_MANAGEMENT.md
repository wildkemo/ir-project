# User Management — RepoMind AI

## Overview

Authenticated users can manage profiles, preferences, favorites, and view activity history. All features extend the existing architecture without replacing localStorage profile wizard or search engines.

## User Profile

| Field | Type | Editable |
|---|---|---|
| `username` | string | Yes |
| `email` | string | At registration |
| `avatar` | URL string | Yes |
| `bio` | text | Yes |
| `role` | User / Admin | Admin only (future) |
| `is_active` | boolean | System |
| `is_verified` | boolean | System |

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/auth/me` | Current user |
| `PATCH` | `/users/me` | Update username, avatar, bio |

## Preferences

Stored in PostgreSQL and **integrated with the recommendation engine** when the user is authenticated:

| Field | Maps to profile recommender |
|---|---|
| `experience_level` | `level` |
| `project_type` | `project_type` |
| `goal` | `goal` |
| `repo_kind` | `repo_kind` |
| `complexity` | `complexity` |
| `languages[]` | first → `language` |
| `preferred_license` | search filter (future) |
| `topics[]` | stored for personalization |
| `frameworks[]` | stored for personalization |

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/users/preferences` | Read preferences |
| `PUT` | `/users/preferences` | Replace preferences |

When a signed-in user calls `POST /search/` or `POST /profile/recommend` without an explicit profile, stored DB preferences are merged automatically.

## Favorites

Stores **repository identifiers only** (`owner/repo`). Metadata is resolved from `processed.json` at display time.

| Method | Path | Description |
|---|---|---|
| `GET` | `/users/favorites` | List favorites |
| `POST` | `/users/favorites` | Add favorite |
| `DELETE` | `/users/favorites/{owner/repo}` | Remove favorite |

Frontend: **Save** button on `RepoCard` when signed in.

## History

### Search History

Recorded when authenticated users run hybrid search.

| Field | Description |
|---|---|
| `query` | Search string |
| `search_type` | e.g. `hybrid` |
| `result_count` | Number of results |
| `created_at` | Timestamp |

### Recommendation History

Recorded for profile recommendations and similar-repo requests.

| Field | Description |
|---|---|
| `repo_identifier` | `owner/repo` |
| `recommendation_score` | Score if available |
| `recommendation_reason` | Why recommended text |
| `created_at` | Timestamp |

### AI Usage History

Recorded for authenticated AI feature calls:

| Request type | Source |
|---|---|
| `explain_repository` | Project explainer, advisor explain |
| `repository_summary` | Advisor summary |
| `compare_repositories` | Advisor compare |
| `learning_roadmap` | Advisor/RAG roadmap |
| `rag_explain` | Ollama RAG explain |

| Field | Description |
|---|---|
| `request_type` | Feature name |
| `repo_identifier` | Target repo |
| `model` | LLM model or rule-based |
| `latency_ms` | Request duration |
| `created_at` | Timestamp |

### History Endpoints

| Method | Path |
|---|---|
| `GET` | `/users/history/search` |
| `GET` | `/users/history/recommendations` |
| `GET` | `/users/history/ai` |

## Frontend Views

| View | Component |
|---|---|
| Login | `LoginPage.jsx` |
| Register | `RegisterPage.jsx` |
| Profile | `UserProfilePanel.jsx` |
| Favorites | `FavoritesPanel.jsx` |
| History | `HistoryPanel.jsx` |

Navigation is in the top bar of `App.jsx`. Existing search/profile wizard flow is unchanged for anonymous users.

## Validation

All inputs validated via Pydantic:

- Usernames: `[a-zA-Z0-9_]{3,50}`
- Emails: standard email format
- Repository IDs: `owner/repo` pattern
- Search queries: max 500 characters

## Coexistence with Profile Wizard

| Mode | Profile source |
|---|---|
| Anonymous | `localStorage` via ProfileWizard |
| Authenticated | DB preferences + optional wizard |
| Authenticated + wizard | Request profile takes precedence |

The recommendation engine (`smart_profile_recommender_v2.py`) logic is **unchanged** — only the profile payload source is extended.
