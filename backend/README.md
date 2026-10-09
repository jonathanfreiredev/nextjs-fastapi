# Backend — FastAPI

The API for the [Next.js + FastAPI Starter](../README.md). It handles user accounts, authentication, and profile management on top of an async SQLAlchemy / PostgreSQL stack.

Authentication is built on [**FastAPI Users**](https://fastapi-users.github.io/fastapi-users/), which provides registration, login, email verification and password reset out of the box (OAuth providers are a planned addition).

## Tech stack

- **FastAPI** — HTTP layer
- **FastAPI Users** (SQLAlchemy adapter) — registration, login, email verification, password reset
- **SQLAlchemy 2.0** (async) with **asyncpg** — ORM and driver
- **Alembic** — database migrations
- **Pydantic v2 / pydantic-settings** — schemas and configuration
- **PyJWT** (RS256) with **cryptography** — signing access tokens
- **pwdlib** (Argon2 + bcrypt, via FastAPI Users) — password hashing
- **uv** — dependency management
- **ruff** — linting and formatting

## Project structure

```
backend/
├── app/
│   ├── auth/
│   │   ├── backend.py         # JWT strategy (RS256 + kid), transport, FastAPIUsers
│   │   ├── constants.py       # Algorithm and token lifetimes
│   │   ├── email.py           # Email sender (console in development)
│   │   ├── keys.py            # RSA key loading, JWKS and key id
│   │   ├── router.py          # /auth endpoints (login, register, verify, reset)
│   │   ├── schemas.py         # UserRead / UserCreate / UserUpdate
│   │   └── users.py           # UserManager + SQLAlchemy user adapter
│   ├── users/
│   │   ├── models.py          # User ORM model
│   │   └── router.py          # /users endpoints (me, change password)
│   ├── db/
│   │   ├── session.py         # Async engine + session factory
│   │   └── models.py          # Declarative Base and BaseModel (id, timestamps)
│   ├── settings.py            # Settings loaded from .env
│   └── main.py                # FastAPI app, routers, JWKS endpoint, CORS
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

# Symmetric secret for email-verification and password-reset tokens
AUTH_SECRET=change-me
```

| Variable          | Required | Default                 | Description                                                        |
| ----------------- | -------- | ----------------------- | ------------------------------------------------------------------ |
| `DATABASE_URL`    | Yes      | –                       | Async connection string. Must use the `postgresql+asyncpg://` driver. |
| `AUTH_SECRET`     | Yes      | –                       | Symmetric secret for the email-verification and password-reset tokens. Generate with `openssl rand -hex 32`. |
| `ENV`             | No       | `development`           | `development` enables SQL echo; anything else disables debug mode.  |
| `FRONTEND_URL`    | No       | `http://localhost:3000` | Base URL of the frontend, used to build the links sent by email.    |
| `JWT_PRIVATE_KEY` | No       | –                       | PEM contents of the RSA private key. When unset in development, `keys/private.pem` is used, or an ephemeral key is generated if missing. |

Settings are defined in `app/settings.py` and loaded from `backend/.env`. In production, set `JWT_PRIVATE_KEY` and `AUTH_SECRET` from your secret store instead of shipping them in files.

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

- **Integration tests** (`tests/integration/`) exercise the API **through its HTTP interface**: routing, validation, dependencies and a real PostgreSQL database, using `httpx`'s ASGI transport. They cover the whole auth surface (register, login, email verification, password reset, profile updates and password change). No server needs to be running. They are not full end-to-end tests — the network is in-process and there is no frontend or browser.
- **Unit tests** (`tests/unit/`) cover a single function in isolation, with no database.

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

Protected endpoints require an `Authorization: Bearer <access_token>` header.

| Method | Path                          | Auth | Description                                    |
| ------ | ----------------------------- | :--: | ---------------------------------------------- |
| POST   | `/auth/register`              |  –   | Create an account (unverified) and email a verification link |
| POST   | `/auth/jwt/login`             |  –   | Log in (form-encoded) and return an access token |
| POST   | `/auth/jwt/logout`            |  ✓   | Log out (no-op for JWT; the client drops the token) |
| POST   | `/auth/request-verify-token`  |  –   | (Re)send the email-verification link           |
| POST   | `/auth/verify`                |  –   | Verify an email with the token from the link   |
| POST   | `/auth/forgot-password`       |  –   | Request a password-reset email                 |
| POST   | `/auth/reset-password`        |  –   | Set a new password with the reset token        |
| GET    | `/.well-known/jwks.json`      |  –   | Public keys used to verify access tokens       |
| GET    | `/users/me`                   |  ✓   | Return the current user                        |
| PATCH  | `/users/me`                   |  ✓   | Update name / email                            |
| PUT    | `/users/me/password/`         |  ✓   | Change the password (requires the current one) |

### Request / response examples

**POST `/auth/register`**

```json
{ "email": "jane@example.com", "password": "supersecret", "full_name": "Jane Doe" }
```

Responds `201` with the created user (`is_verified: false`) and sends a verification email.

**POST `/auth/jwt/login`** — `application/x-www-form-urlencoded`

```
username=jane@example.com&password=supersecret
```

Response:

```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

**POST `/auth/verify`**

```json
{ "token": "<token from the verification link>" }
```

**POST `/auth/forgot-password`** → `{ "email": "jane@example.com" }`, then **POST `/auth/reset-password`**

```json
{ "token": "<token from the reset link>", "password": "newsecret123" }
```

**PATCH `/users/me`**

```json
{ "full_name": "Jane Smith", "email": "jane.smith@example.com" }
```

**PUT `/users/me/password/`**

```json
{ "old_password": "supersecret", "new_password": "evensecreter" }
```

## Authentication notes

- **FastAPI Users** owns the user lifecycle: registration, email verification, password reset and the user CRUD routes. The glue lives in `app/auth/` (`users.py`, `backend.py`, `router.py`).
- Access tokens are **RS256** JWTs (asymmetric), valid for `ACCESS_TOKEN_LIFETIME_SECONDS` (24 hours, in `app/auth/constants.py`). The payload carries `sub` (the user **id**), `aud` (`fastapi-users:auth`) and `exp`; the header carries a `kid`. The private key lives **only in the backend**; the public key is served at `/.well-known/jwks.json` so the frontend can verify tokens without being able to sign them.
- The RSA key pair is loaded in `app/auth/keys.py`: from `JWT_PRIVATE_KEY`, else `keys/private.pem`, else an ephemeral key in development. Generate a stable pair with `uv run python scripts/generate_keys.py`.
- **There are no refresh tokens.** A JWT is valid until it expires and cannot be invalidated server-side, so "log out" simply means the client discards the token. This is FastAPI Users' JWT model; if you need instant revocation later, switch to its Database or Redis strategy.
- Email verification and password reset use short-lived JWTs signed with `AUTH_SECRET` (24 hours for verification, 1 hour for reset). Changing the email resets `is_verified` to `false`.
- The development email sender (`app/auth/email.py`) writes the link to the logs. Replace `send_email` with a real provider (Resend, SES, SMTP...) in production.
- `current_active_user` / `current_verified_user` (`app/auth/backend.py`) are the dependencies that resolve a bearer token to a user; the former rejects inactive accounts, the latter also requires a verified email.

## Conventions

- Imports are **absolute** and rooted at the `app` package (`from app.auth.users import ...`). Avoid relative imports so the dependency direction stays easy to read.
- Every directory is a regular package with an empty `__init__.py`. Nothing is re-exported there on purpose, so import cycles remain visible instead of being hidden behind package-level imports.
- The `app` package is imported from the working directory (`backend/`). Run the CLI commands from `backend/` so `app` is on `sys.path`.

## CORS

Allowed origins are configured in `app/main.py`. The default list includes `http://localhost:3000` for local development — update it before deploying.

## Notes

- `app/db/models.py` defines a shared `BaseModel` with a UUID primary key plus `created_at`, `updated_at`, and `deleted_at` columns for every table.
- The `User` model adds `full_name` and the fields FastAPI Users expects: `is_active`, `is_superuser`, `is_verified`.
- Passwords are hashed with Argon2 via FastAPI Users' `PasswordHelper`.
