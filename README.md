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
│   │   ├── auth/            # Signup, login, token handling, logout-all
│   │   ├── users/           # User model, schemas, service, router
│   │   ├── db/              # Async engine, session, base model
│   │   ├── dependencies.py  # get_current_user / get_current_active_user
│   │   ├── settings.py      # Pydantic settings (reads .env)
│   │   └── main.py          # App entrypoint + CORS
│   ├── alembic/             # Database migrations
│   ├── start-database.sh    # Local PostgreSQL container helper
│   └── pyproject.toml       # Dependencies (managed with uv)
│
├── frontend/                # Next.js application
│   ├── app/                 # App Router pages, layouts, API routes
│   ├── components/          # UI + auth components (shadcn/ui based)
│   ├── server/              # Server actions, schemas, session helpers
│   ├── lib/                 # Env validation, safe-action client, utils
│   └── package.json         # Dependencies (managed with pnpm)
│
└── LICENSE                  # MIT
```

## Prerequisites

- **Node.js** 20+ and **pnpm**
- **Python** 3.14+ and [**uv**](https://docs.astral.sh/uv/)
- **Docker** or **Podman** (for the local database), or an existing PostgreSQL instance

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
| `NODE_ENV`    | No       | Set automatically by Next.js.                          |

Environment variables in the frontend are validated at startup with `@t3-oss/env-nextjs` (`lib/env.js`).

## API reference

All endpoints live on the FastAPI backend. Protected routes expect an `Authorization: Bearer <token>` header.

| Method | Path                  | Auth | Description                          |
| ------ | --------------------- | :--: | ------------------------------------ |
| POST   | `/auth/signup`        |  –   | Create an account and return a token |
| POST   | `/auth/login`         |  –   | Authenticate and return a token      |
| POST   | `/auth/update-token`  |  ✓   | Issue a fresh token for the current user |
| POST   | `/auth/logout-all`    |  ✓   | Invalidate all previously issued tokens |
| GET    | `/users/me/`          |  ✓   | Return the current user              |
| PUT    | `/users/me/`          |  ✓   | Update name / email (and refresh the token) |
| PUT    | `/users/me/password/` |  ✓   | Change password                      |

## Authentication flow

1. The user signs up or logs in through a **server action**.
2. The action calls the backend, receives a JWT, and stores it in an **HTTP-only cookie** (`access_token`).
3. `getSession()` (`frontend/server/auth/auth.lib.ts`) reads and decodes the cookie to build the session used by layouts and pages.
4. Protected server actions use `protectedProcedure`, which rejects the request when there is no valid session and forwards the token to the backend.
5. "Log out everywhere" bumps `tokens_valid_after` on the user, invalidating every token issued before that moment.

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

## License

[MIT](./LICENSE) © 2026 Jonathan Freire
