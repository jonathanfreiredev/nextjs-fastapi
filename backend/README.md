# Backend — FastAPI

The API for the [Next.js + FastAPI Starter](../README.md). It handles user accounts, JWT authentication, and profile management on top of an async SQLAlchemy / PostgreSQL stack.

## Tech stack

- **FastAPI** — HTTP layer
- **SQLAlchemy 2.0** (async) with **asyncpg** — ORM and driver
- **Alembic** — database migrations
- **Pydantic v2 / pydantic-settings** — schemas and configuration
- **PyJWT** (RS256) with **cryptography** — signing access tokens
- **pwdlib[argon2]** — password hashing
- **uv** — dependency management
- **ruff** — linting and formatting

## Project structure

```
backend/
├── app/
│   ├── auth/
│   │   ├── constants.py       # Algorithm and access/refresh TTLs
│   │   ├── keys.py            # RSA key loading, JWKS and key id
│   │   ├── models.py          # RefreshToken model (stored hashed)
│   │   ├── refresh.py         # Refresh token issue/consume/revoke (rotation)
│   │   ├── router.py          # /auth endpoints
│   │   ├── schemas.py         # Token + RefreshTokenRequest schemas
│   │   ├── security.py        # Password hashing (Argon2)
│   │   └── service.py         # Token pair creation, verification, signup/login
│   ├── users/
│   │   ├── models.py          # User ORM model
│   │   ├── schemas.py         # Create/Update/Login DTOs
│   │   ├── service.py         # User CRUD and password updates
│   │   └── router.py          # /users endpoints
│   ├── db/
│   │   ├── session.py         # Async engine + session factory
│   │   └── models.py          # Declarative Base and BaseModel (id, timestamps)
│   ├── dependencies.py        # get_current_user / get_current_active_user
│   ├── settings.py            # Settings loaded from .env
│   └── main.py                # FastAPI app, routers, CORS
├── alembic/                   # Migrations (async env.py)
├── scripts/
│   └── generate_keys.py       # Generate the RSA key pair
├── alembic.ini
├── start-database.sh          # Starts a local PostgreSQL container
├── pyproject.toml
└── .python-version            # 3.14
```

## Requirements

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/)
- Docker or Podman (for the local database), or a PostgreSQL server you can point `DATABASE_URL` at

## Setup

```bash
cd backend

# Install dependencies into .venv
uv sync

# Generate the RSA key pair used to sign JWTs (writes keys/, gitignored)
uv run python scripts/generate_keys.py

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
```

| Variable          | Required | Default       | Description                                                        |
| ----------------- | -------- | ------------- | ------------------------------------------------------------------ |
| `DATABASE_URL`    | Yes      | –             | Async connection string. Must use the `postgresql+asyncpg://` driver. |
| `ENV`             | No       | `development` | `development` enables SQL echo; anything else disables debug mode.  |
| `JWT_PRIVATE_KEY` | No       | –             | PEM contents of the RSA private key. When unset in development, `keys/private.pem` is used, or an ephemeral key is generated if missing. |

Settings are defined in `app/settings.py` and loaded from `backend/.env`. In production, set `JWT_PRIVATE_KEY` from your secret store instead of shipping the key file.

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

- **Integration tests** (`tests/integration/`) exercise the API **through its HTTP interface**: routing, validation, dependencies, services and a real PostgreSQL database, using `httpx`'s ASGI transport. No server needs to be running. They are not full end-to-end tests — the network is in-process and there is no frontend or browser.
- **Unit tests** (`tests/unit/`) cover a single function in isolation. Collaborators that touch I/O (the database lookup) are replaced with doubles, so they run in milliseconds and need **no database at all**.

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

Alembic is configured for async migrations (`alembic/env.py`) and imports the models so autogenerate can detect changes. The initial migration creates the `users` table.

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

Protected endpoints require an `Authorization: Bearer <token>` header.

| Method | Path                  | Auth | Description                           |
| ------ | --------------------- | :--: | ------------------------------------- |
| POST   | `/auth/signup`        |  –   | Create a user and return a token pair |
| POST   | `/auth/login`         |  –   | Authenticate and return a token pair  |
| POST   | `/auth/refresh`       |  –   | Exchange a refresh token for a new pair (rotates it) |
| POST   | `/auth/logout`        |  –   | Revoke a refresh token                |
| POST   | `/auth/logout-all`    |  ✓   | Revoke every refresh token for the user |
| GET    | `/.well-known/jwks.json` | – | Public keys used to verify access tokens |
| GET    | `/users/me/`          |  ✓   | Return the current user               |
| PUT    | `/users/me/`          |  ✓   | Update name / email                   |
| PUT    | `/users/me/password/` |  ✓   | Change the password                   |

### Request / response examples

**POST `/auth/signup`**

```json
{ "full_name": "Jane Doe", "email": "jane@example.com", "password": "supersecret" }
```

Response:

```json
{ "access_token": "<jwt>", "refresh_token": "<opaque>", "token_type": "bearer" }
```

**PUT `/users/me/`**

```json
{ "full_name": "Jane Smith", "email": "jane.smith@example.com" }
```

**PUT `/users/me/password/`**

```json
{ "old_password": "supersecret", "new_password": "evensecreter" }
```

## Authentication notes

- Access tokens are signed with **RS256** (asymmetric) and expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (15 minutes, in `app/auth/constants.py`). The payload carries `sub` (email), `name`, `iat`, and `exp`. The private key lives **only in the backend**; the public key is served at `/.well-known/jwks.json` so the frontend can verify tokens without being able to sign them.
- The RSA key pair is loaded in `app/auth/keys.py`: from `JWT_PRIVATE_KEY`, else `keys/private.pem`, else an ephemeral key in development. Generate a stable pair with `uv run python scripts/generate_keys.py`.
- Refresh tokens are **opaque** random values, never exposed in decoded form: only a SHA-256 hash is stored in the `refresh_tokens` table. They live for `REFRESH_TOKEN_EXPIRE_DAYS` (30 days) and are **rotated** — each `/auth/refresh` revokes the used token and issues a new one, so a replayed token is rejected.
- Every user has a `tokens_valid_after` timestamp. Any access token with an `iat` earlier than that value is rejected, which is how `logout-all` invalidates outstanding access tokens. Both values use **whole seconds** (the precision of a JWT `iat`), so a token issued in the same second as the logout is not invalidated — an inherent limit of second-precision tokens.
- `get_current_user` resolves the bearer token to a `UserDto`, and `get_current_active_user` additionally rejects disabled accounts.

## Conventions

- Imports are **absolute** and rooted at the `app` package (`from app.users.service import ...`). Avoid relative imports so the dependency direction stays easy to read.
- Every directory is a regular package with an empty `__init__.py`. Nothing is re-exported there on purpose, so import cycles remain visible instead of being hidden behind package-level imports.
- Dependencies flow in one direction: `router → service → security / models / schemas`. Password hashing lives in `app/auth/security.py`, which both `auth` and `users` share, so `app/users/service.py` never imports `app/auth/service.py`.
- The `app` package is imported from the working directory (`backend/`). Run the CLI commands from `backend/` so `app` is on `sys.path`.

## CORS

Allowed origins are configured in `app/main.py`. The default list includes `http://localhost:3000` for local development — update it before deploying.

## Notes

- `app/db/models.py` defines a shared `BaseModel` with a UUID primary key plus `created_at`, `updated_at`, and `deleted_at` columns for every table.
- Passwords are hashed with Argon2 via `PasswordHash.recommended()`.
