# Backend — FastAPI

The API for the [Next.js + FastAPI Starter](../README.md). It exposes the application's domain data (the user profile) on top of an async SQLAlchemy / PostgreSQL stack.

Authentication is delegated to [**Supabase Auth**](https://supabase.com/docs/guides/auth), which owns credentials, email verification, social login and sessions. This service is a **resource server**: it verifies the Supabase access token (an asymmetric JWT) against the project's **JWKS** and provisions a local profile the first time it sees a user. It never issues tokens or stores passwords.

## Tech stack

- **FastAPI** — HTTP layer
- **SQLAlchemy 2.0** (async) with **asyncpg** — ORM and driver
- **Alembic** — database migrations
- **Pydantic v2 / pydantic-settings** — schemas and configuration
- **PyJWT** with **cryptography** — verifying Supabase access tokens (RS256/ES256)
- **uv** — dependency management
- **ruff** — linting and formatting

## Project structure

```
backend/
├── app/
│   ├── auth/
│   │   ├── verifier.py        # Verify a Supabase JWT against the project's JWKS
│   │   └── dependencies.py    # Bearer token -> TokenClaims
│   ├── users/
│   │   ├── models.py          # User (profile) ORM model
│   │   ├── schemas.py         # UserRead / UserUpdate
│   │   ├── service.py         # Just-in-time profile provisioning
│   │   ├── dependencies.py    # TokenClaims -> local User
│   │   └── router.py          # /users endpoints (me)
│   ├── db/
│   │   ├── session.py         # Async engine + session factory
│   │   └── models.py          # Declarative Base and BaseModel (id, timestamps)
│   ├── settings.py            # Settings loaded from .env
│   └── main.py                # FastAPI app, routers, CORS
├── alembic/                   # Migrations (async env.py)
├── alembic.ini
├── start-database.sh          # Starts a local PostgreSQL container
├── pyproject.toml
└── .python-version            # 3.14
```

## Requirements

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/)
- Docker or Podman (for the local database), or a PostgreSQL server you can point `DATABASE_URL` at
- A **Supabase project** (see the [frontend README](../frontend/README.md) for the auth setup)

## Setup

```bash
cd backend

# Install dependencies into .venv
uv sync

# Create your environment file
cp .env.example .env

# Start PostgreSQL
./start-database.sh

# Apply migrations
uv run alembic upgrade head
```

`start-database.sh` reads `DATABASE_URL` from `.env`, extracts the database name, port, and password, and runs a matching `postgres` container. If the password is still the default `password`, it offers to generate a random one and updates `.env` for you.

## Environment variables

Create `backend/.env`:

```dotenv
# DATABASE
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/app

# Supabase project URL (the issuer and JWKS are derived from it)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_JWT_AUDIENCE=authenticated
```

| Variable                | Required | Default                 | Description                                                          |
| ----------------------- | -------- | ----------------------- | -------------------------------------------------------------------- |
| `DATABASE_URL`          | Yes      | –                       | Async connection string. Must use the `postgresql+asyncpg://` driver. |
| `SUPABASE_URL`          | Yes      | –                       | Supabase project URL. The issuer (`<url>/auth/v1`) and JWKS (`<url>/auth/v1/.well-known/jwks.json`) are derived from it. |
| `SUPABASE_JWT_AUDIENCE` | No       | `authenticated`         | Audience claim the access tokens carry.                              |
| `ENV`                   | No       | `development`           | `development` enables SQL echo.                                      |
| `FRONTEND_URL`          | No       | `http://localhost:3000` | Base URL of the frontend, used for redirects and documentation.      |

Settings are defined in `app/settings.py` and loaded from `backend/.env`.

## Running the server

```bash
# Development (auto-reload) — http://localhost:8000
uv run fastapi dev

# Production
uv run fastapi run
```

The OpenAPI docs are at `/docs`, and the raw schema at `/openapi.json`.

## Linting and formatting

The project uses [ruff](https://docs.astral.sh/ruff/) for both linting and formatting, configured in `pyproject.toml`.

```bash
# Lint
uv run ruff check .

# Lint and auto-fix
uv run ruff check --fix .

# Format
uv run ruff format .
```

## Tests

The suite has two layers, split by directory:

- **Integration tests** (`tests/integration/`) exercise the API **through its HTTP interface** against a real PostgreSQL database, using `httpx`'s ASGI transport. They forge Supabase-style access tokens with a local RSA key (`tests/auth_stub.py`), so no Supabase project is needed and the real signature, issuer, audience and expiry checks still run.
- **Unit tests** (`tests/unit/`) cover single functions in isolation, with no database (token verification edge cases).

Run everything:

```bash
uv run pytest
```

Run one layer:

```bash
uv run pytest tests/unit          # no database required
uv run pytest tests/integration   # needs the test database
```

### Test database

The integration tests use a dedicated PostgreSQL database. Create it once, next to your development one:

```bash
# the container name is "<db_name>-postgres" (see start-database.sh)
docker exec <db_name>-postgres createdb -U postgres app_test
```

By default they connect to `app_test` on the same host as `DATABASE_URL`; set `TEST_DATABASE_URL` to point somewhere else. Each test creates the tables before it runs and drops them afterwards, so it never touches your development data.

## Database migrations

Alembic is configured for async migrations (`alembic/env.py`) and imports the models so autogenerate can detect changes.

```bash
# Generate a migration after changing a model
uv run alembic revision --autogenerate -m "describe change"

# Apply all pending migrations
uv run alembic upgrade head

# Roll back one migration
uv run alembic downgrade -1
```

When you add a new model, import it in `alembic/env.py` so it is included in autogenerate.

## API reference

Protected endpoints require an `Authorization: Bearer <supabase_access_token>` header.

| Method | Path         | Auth | Description                                          |
| ------ | ------------ | :--: | ---------------------------------------------------- |
| GET    | `/users/me`  |  ✓   | Return the current profile (provisions it on first use) |
| PATCH  | `/users/me`  |  ✓   | Update the profile name                              |

### Request / response examples

**PATCH `/users/me`** — the name is domain data owned by this service; the email lives in Supabase and is changed from the client.

```json
{ "full_name": "Jane Smith" }
```

## Authentication notes

- **Supabase Auth owns the user lifecycle**: signup, email verification, password reset, social login and sessions. This service stores no passwords and issues no tokens.
- Access tokens are **asymmetric JWTs** (RS256 by default, ES256 also accepted). `app/auth/verifier.py` validates the signature against the project's **JWKS**, plus the `iss`, `aud` and `exp` claims, so tokens from another project — or expired ones — are rejected.
- **Just-in-time provisioning**: the first time a valid token is seen, `app/users/service.py` creates the local profile keyed by `supabase_user_id` (the token's `sub`, a stable UUID). Later requests keep the mirrored email in sync. The profile's own `id` is what you should use for relations.
- `app/auth/dependencies.py` resolves the bearer token into `TokenClaims`; `app/users/dependencies.py` resolves those claims into a local `User`. Inactive or unverified checks are handled by Supabase at authentication time, not here.

## Conventions

- Imports are **absolute** and rooted at the `app` package (`from app.users.service import ...`). Avoid relative imports so the dependency direction stays easy to read.
- Every directory is a regular package with an empty `__init__.py`. Nothing is re-exported there on purpose, so import cycles remain visible instead of being hidden behind package-level imports.
- The `app` package is imported from the working directory (`backend/`). Run the CLI commands from `backend/` so `app` is on `sys.path`.

## CORS

Allowed origins are configured in `app/main.py`. The default list includes `http://localhost:3000` for local development — update it before deploying.

## Notes

- `app/db/models.py` defines a shared `BaseModel` with a UUID primary key plus `created_at`, `updated_at`, and `deleted_at` columns for every table.
- The `User` model is a **profile**: `supabase_user_id` (unique, links to Supabase), `email`, `full_name`. Add your own fields and relations on top of `id`.
