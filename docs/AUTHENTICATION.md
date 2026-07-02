# Authentication — RepoMind AI

## Overview

User authentication uses **JWT access tokens** + **refresh tokens** stored in PostgreSQL (hashed). Passwords are hashed with **Argon2id**.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create account |
| `POST` | `/auth/login` | No | Issue tokens |
| `POST` | `/auth/refresh` | No | Rotate refresh token |
| `POST` | `/auth/logout` | No | Revoke refresh token |
| `GET` | `/auth/me` | Bearer | Current user |

## Token Flow

```
Register/Login
  → access_token (JWT, short-lived)
  → refresh_token (opaque, stored hashed in DB)

API requests
  → Authorization: Bearer <access_token>

Access expired
  → POST /auth/refresh { refresh_token }
  → new access + refresh tokens (rotation)

Logout
  → POST /auth/logout { refresh_token }
  → refresh token revoked in DB
```

## JWT Claims

| Claim | Description |
|---|---|
| `sub` | User UUID |
| `exp` | Expiry timestamp |
| `type` | `"access"` |
| `role` | Role name (`User` / `Admin`) |

## Environment Variables

| Variable | Default |
|---|---|
| `JWT_SECRET_KEY` | **Required** — no default in production |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |

## Security

| Control | Implementation |
|---|---|
| Password hashing | Argon2id via `argon2-cffi` |
| SQL injection | SQLAlchemy ORM parameterization |
| Input validation | Pydantic v2 schemas |
| Rate limiting | `slowapi` on register/login/refresh |
| Secrets | `.env` only — see `.env.example` |
| Logging | Structured logs — **never** passwords, JWTs, or API keys |

## Roles

| Role | Access |
|---|---|
| `User` | Standard features |
| `Admin` | Elevated routes via `require_admin` dependency |

Default role on registration: **User**.

## Frontend Integration

- Tokens stored in `localStorage` (`repomind_access_token`, `repomind_refresh_token`)
- Axios interceptors attach `Authorization: Bearer` header
- `AuthContext` provides `login`, `register`, `logout`, `user`

## Rate Limits

| Endpoint | Limit |
|---|---|
| `/auth/register` | 10/minute |
| `/auth/login` | 20/minute |
| `/auth/refresh` | 30/minute |

## Files

| File | Role |
|---|---|
| `backend/security/password.py` | Argon2 hashing |
| `backend/security/jwt.py` | Token create/decode |
| `backend/security/deps.py` | `get_current_user`, `require_admin` |
| `backend/core/auth_service.py` | Register/login/refresh logic |
| `backend/api/auth.py` | REST routes |
