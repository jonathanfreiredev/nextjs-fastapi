# Next.js + FastAPI Starter

A full-stack starter template pairing a **Next.js 16** frontend with a **FastAPI** backend, wired together with a complete JWT authentication flow, server actions, and a PostgreSQL database.

The template ships with signup, login, email verification, password reset, profile editing and password change as working examples, so you can start building features on top of a real, end-to-end setup instead of a blank page. Authentication is powered by [**FastAPI Users**](https://fastapi-users.github.io/fastapi-users/).

## Tech stack

| Layer      | Technology                                                                        |
| ---------- | --------------------------------------------------------------------------------- |
| Frontend   | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Motion  |
| Forms      | React Hook Form, Zod, next-safe-action                                             |
| Backend    | FastAPI, SQLAlchemy 2 (async), Pydantic v2                                          |
| Database   | PostgreSQL, Alembic migrations                                                     |
| Auth       | FastAPI Users, JWT (RS256) with a JWKS endpoint, Argon2 password hashing, HTTP-only cookies |

## Architecture

```
┌──────────────────────────┐        ┌──────────────────────────┐        ┌──────────────┐
│  Browser                 │        │  Next.js (server)        │        │  FastAPI     │
│                          │        │                          │        │              │
│  React components  ──────┼───────▶│  server actions  ────────┼───────▶│  routers     │
│  (client)                │        │  (auth.actions, etc.)    │        │  services    │
│                          │◀───────┼──  HTTP-only cookie      │◀───────┼──  JWT       │
│  session via getSession  │        │  (access_token)          │        │  SQLAlchemy  │
└──────────────────────────┘        └──────────────────────────┘        └──────┬───────┘
                                                                              │
                                                                       ┌──────▼───────┐
                                                                       │  PostgreSQL  │
                                                                       └──────────────┘
```

The browser never talks to FastAPI directly. Server-side actions in `frontend/server/` call the backend, store the JWT in an HTTP-only cookie, and the Next.js server reads it back to build the session.

## Repository structure

```
.
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── auth/            # FastAPI Users glue: manager, JWT strategy, routers
│   │   ├── users/           # User model + /users router
│   │   ├── db/              # Async engine, session, base model
│   │   ├── settings.py      # Pydantic settings (reads .env)
│   │   └── main.py          # App entrypoint + CORS
│   ├── alembic/             # Database migrations
│   ├── tests/               # Unit + integration tests
│   ├── Dockerfile           # Dev image (+ production stage)
│   ├── start-database.sh    # Local PostgreSQL container helper
│   └── pyproject.toml       # Dependencies (managed with uv)
│
├── frontend/                # Next.js application
│   ├── app/                 # App Router pages, layouts, API routes
│   ├── components/          # UI + auth components (shadcn/ui based)
│   ├── server/              # Server actions, schemas, session helpers
│   ├── lib/                 # Env validation, safe-action client, utils
│   ├── Dockerfile           # Dev image
│   └── package.json         # Dependencies (managed with pnpm)
│
├── .github/workflows/       # CI (backend + frontend)
├── docker-compose.yml       # Local development stack
└── LICENSE                  # MIT
```

## Prerequisites

- **Node.js** 20+ and **pnpm**
- **Python** 3.14+ and [**uv**](https://docs.astral.sh/uv/)
- **Docker** or **Podman** if you want the containerized stack (or a local database via `start-database.sh`)

## Getting started

### 1. Backend

```bash
cd backend

# Install dependencies
uv sync

# Generate the RSA key pair used to sign JWTs
uv run python scripts/generate_keys.py

# Create your environment file
cp .env.example .env

# Start a local PostgreSQL container (reads DATABASE_URL from .env)
./start-database.sh

# Apply database migrations
uv run alembic upgrade head

# Run the dev server on http://localhost:8000
uv run fastapi dev
```

Interactive API docs are available at http://localhost:8000/docs.

### 2. Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Create your environment file
cp .env.example .env

# Run the dev server on http://localhost:3000
pnpm dev
```

Open http://localhost:3000 and sign up. You will receive a verification email (printed to the backend logs in development) — verify it, then log in.

## Run with Docker

`docker-compose.yml` is a **local development** stack: PostgreSQL plus the API and the web app, with the source mounted and the dev servers running with reload.

```bash
docker compose up
```

A one-shot `migrate` service runs `alembic upgrade head` before the API starts, so the schema is always up to date.

Deployment is not handled here: the frontend goes to Vercel (which builds it natively) and the backend to its own service. The `backend/Dockerfile` also has a production stage if you deploy it as a container.

## Environment variables

### `backend/.env`

| Variable          | Required | Description                                                                 |
| ----------------- | -------- | --------------------------------------------------------------------------- |
| `DATABASE_URL`    | Yes      | Async PostgreSQL URL, e.g. `postgresql+asyncpg://postgres:password@localhost:5432/app`. |
| `AUTH_SECRET`     | Yes      | Symmetric secret for the email-verification and password-reset tokens.      |
| `ENV`             | No       | `development` (default) or `production`. Enables SQL echo when in development. |
| `FRONTEND_URL`    | No       | Base URL of the frontend, used to build the links sent by email.            |
| `JWT_PRIVATE_KEY` | No       | PEM contents of the RSA signing key. Unset in development: `keys/private.pem` is used, or an ephemeral key is generated. |

### `frontend/.env`

| Variable      | Required | Description                                            |
| ------------- | -------- | ------------------------------------------------------ |
| `BACKEND_URL` | Yes      | Base URL of the FastAPI backend, e.g. `http://localhost:8000`. |
| `NODE_ENV`    | No       | Set automatically by Next.js.                          |

Environment variables in the frontend are validated at startup with `@t3-oss/env-nextjs` (`lib/env.js`).

## API reference

All endpoints live on the FastAPI backend. Protected routes expect an `Authorization: Bearer <access_token>` header.

| Method | Path                          | Auth | Description                          |
| ------ | ----------------------------- | :--: | ------------------------------------ |
| POST   | `/auth/register`              |  –   | Create an account (unverified) and email a verification link |
| POST   | `/auth/jwt/login`             |  –   | Log in (form-encoded) and return an access token |
| POST   | `/auth/request-verify-token`  |  –   | (Re)send the email-verification link |
| POST   | `/auth/verify`                |  –   | Verify an email                         |
| POST   | `/auth/forgot-password`       |  –   | Request a password-reset email       |
| POST   | `/auth/reset-password`        |  –   | Set a new password with the reset token |
| GET    | `/users/me`                   |  ✓   | Return the current user              |
| PATCH  | `/users/me`                   |  ✓   | Update name / email                  |
| PUT    | `/users/me/password/`         |  ✓   | Change password                      |

The access token is a long-lived JWT (24 hours) signed with RS256; there are no refresh tokens, so a token stays valid until it expires.

## Authentication flow

1. The user signs up or logs in through a **server action**.
2. The action calls the backend. On login, it stores the returned **access token** in a single HTTP-only cookie (`access_token`, 24h JWT).
3. `getSession()` (`frontend/server/auth/auth.lib.ts`) **verifies** the access token's RS256 signature and expiry using the public keys from the backend's `/.well-known/jwks.json`, then fetches `/users/me` for the profile. The frontend never holds the signing key.
4. There are no refresh tokens: when the token expires, the user logs in again.
5. Protected server actions use `protectedProcedure`, which rejects the request when there is no valid session and forwards the access token to the backend.
6. Registration, email verification and password reset are handled by FastAPI Users; the verification and reset links point to pages in `frontend/app/auth/`.

## Common commands

### Backend (`backend/`)

| Command                                            | Description                        |
| -------------------------------------------------- | ---------------------------------- |
| `uv run fastapi dev`                               | Start the dev server with reload   |
| `uv run fastapi run`                               | Start the production server        |
| `uv run alembic revision --autogenerate -m "msg"`  | Create a migration from model changes |
| `uv run alembic upgrade head`                      | Apply migrations                   |
| `uv run alembic downgrade -1`                      | Roll back the last migration        |
| `uv run ruff check .`                              | Lint the backend                   |
| `uv run ruff format .`                             | Format the backend                 |
| `uv run pytest`                                    | Run all backend tests              |
| `uv run pytest tests/unit`                         | Run unit tests (no database needed) |

### Frontend (`frontend/`)

| Command        | Description                     |
| -------------- | ------------------------------- |
| `pnpm dev`     | Start the dev server            |
| `pnpm build`   | Production build                |
| `pnpm start`   | Serve the production build      |
| `pnpm lint`    | Run ESLint                      |

## Continuous integration

GitHub Actions runs two path-filtered workflows, so a change in one app does not trigger the other:

- `.github/workflows/backend.yml` — lints, checks formatting, applies migrations and runs the tests against a PostgreSQL service container.
- `.github/workflows/frontend.yml` — lints, type-checks and builds the Next.js app.

## License

[MIT](./LICENSE) © 2026 Jonathan Freire
