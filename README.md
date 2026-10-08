# Next.js + FastAPI Starter

A full-stack starter template pairing a **Next.js 16** frontend with a **FastAPI** backend, wired together with a complete JWT authentication flow, server actions, and a PostgreSQL database.

The template ships with signup, login, profile editing, password change, token refresh, and "log out everywhere" as working examples, so you can start building features on top of a real, end-to-end setup instead of a blank page.

## Tech stack

| Layer      | Technology                                                                        |
| ---------- | --------------------------------------------------------------------------------- |
| Frontend   | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Motion  |
| Forms      | React Hook Form, Zod, next-safe-action                                             |
| Backend    | FastAPI, SQLAlchemy 2 (async), Pydantic v2                                          |
| Database   | PostgreSQL, Alembic migrations                                                     |
| Auth       | JWT (HS256), Argon2 password hashing, HTTP-only cookies                            |

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
│   │   ├── auth/            # Signup, login, access/refresh tokens
│   │   ├── users/           # User model, schemas, service, router
│   │   ├── db/              # Async engine, session, base model
│   │   ├── dependencies.py  # get_current_user / get_current_active_user
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
│   ├── proxy.ts             # Token refresh on each request
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

Open http://localhost:3000, sign up, and you should land back on the home page authenticated.

## Run with Docker

`docker-compose.yml` is a **local development** stack: PostgreSQL plus the API and the web app, with the source mounted and the dev servers running with reload.

```bash
docker compose up
```

A one-shot `migrate` service runs `alembic upgrade head` before the API starts, so the schema is always up to date.

Deployment is not handled here: the frontend goes to Vercel (which builds it natively) and the backend to its own service. The `backend/Dockerfile` also has a production stage if you deploy it as a container.

## Environment variables

### `backend/.env`

| Variable       | Required | Description                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------- |
| `SECRET_KEY`   | Yes      | Secret used to sign JWTs. Generate one with `openssl rand -hex 32`.         |
| `DATABASE_URL` | Yes      | Async PostgreSQL URL, e.g. `postgresql+asyncpg://postgres:password@localhost:5432/app`. |
| `ENV`          | No       | `development` (default) or `production`. Enables SQL echo when in development. |

### `frontend/.env`

| Variable      | Required | Description                                            |
| ------------- | -------- | ------------------------------------------------------ |
| `BACKEND_URL` | Yes      | Base URL of the FastAPI backend, e.g. `http://localhost:8000`. |
| `JWT_SECRET`  | Yes      | Same value as the backend `SECRET_KEY`; used to verify the session JWT. |
| `NODE_ENV`    | No       | Set automatically by Next.js.                          |

Environment variables in the frontend are validated at startup with `@t3-oss/env-nextjs` (`lib/env.js`).

## API reference

All endpoints live on the FastAPI backend. Protected routes expect an `Authorization: Bearer <access_token>` header.

| Method | Path                  | Auth | Description                          |
| ------ | --------------------- | :--: | ------------------------------------ |
| POST   | `/auth/signup`        |  –   | Create an account and return a token pair |
| POST   | `/auth/login`         |  –   | Authenticate and return a token pair |
| POST   | `/auth/refresh`       |  –   | Exchange a refresh token for a new pair (rotates it) |
| POST   | `/auth/logout`        |  –   | Revoke a refresh token               |
| POST   | `/auth/logout-all`    |  ✓   | Revoke every refresh token for the current user |
| GET    | `/users/me/`          |  ✓   | Return the current user              |
| PUT    | `/users/me/`          |  ✓   | Update name / email                  |
| PUT    | `/users/me/password/` |  ✓   | Change password                      |

The access token is a short-lived JWT (15 minutes); the refresh token is an opaque, single-use value (30 days) stored hashed in the database.

## Authentication flow

1. The user signs up or logs in through a **server action**.
2. The action calls the backend and stores the returned **token pair** in two HTTP-only cookies: `access_token` (15 min JWT) and `refresh_token` (30 days, opaque).
3. `getSession()` (`frontend/server/auth/auth.lib.ts`) **verifies** the access token's signature and expiry to build the session used by layouts and pages.
4. `proxy.ts` runs before rendering: when the access token is expired but a refresh token is present, it calls `/auth/refresh`, rotates the pair, and updates both the request and response cookies so the current render already sees the new tokens.
5. Protected server actions use `protectedProcedure`, which rejects the request when there is no valid session and forwards the access token to the backend.
6. Logout revokes the refresh token; "log out everywhere" revokes every refresh token for the user and bumps `tokens_valid_after`.

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
