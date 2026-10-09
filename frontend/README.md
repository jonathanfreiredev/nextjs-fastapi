# Frontend — Next.js

The web client for the [Next.js + FastAPI Starter](../README.md). It renders the UI, validates forms, and talks to the FastAPI backend through server actions — the browser never sees the JWT directly.

## Tech stack

- **Next.js 16** (App Router) and **React 19**
- **TypeScript**
- **Tailwind CSS 4** with **shadcn/ui** components (base-nova style, Lucide icons)
- **React Hook Form** + **Zod** for forms and validation
- **next-safe-action** for type-safe server actions
- **@t3-oss/env-nextjs** for environment variable validation
- **Motion** for animations, **jose** for verifying the session JWT
- **pnpm** as the package manager

## Project structure

```
frontend/
├── app/
│   ├── (root)/            # Public shell: home page + header layout
│   ├── auth/              # login, signup, forgot-password, reset-password, verify-email
│   ├── profile/           # Protected profile page
│   ├── api/logout/        # Route handler that clears the session cookie
│   ├── layout.tsx         # Root layout (fonts, Toaster)
│   └── globals.css        # Tailwind + theme tokens
├── components/
│   ├── auth/              # Auth, profile, change-password and verification components
│   ├── ui/                # shadcn/ui primitives
│   └── ...                # Header, avatar menu, sidebar, background
├── server/
│   ├── auth/              # Session helper, server actions, schemas, logout service
│   └── users/             # Profile + password server actions and schemas
├── lib/
│   ├── env.js             # Validated env vars
│   ├── safe-action.ts     # Public / protected action clients
│   └── utils.ts           # cn() helper
└── package.json
```

## Requirements

- Node.js 20+
- [pnpm](https://pnpm.io/)
- The backend running (see `../backend/README.md`)

## Setup

```bash
pnpm install
```

Copy the example environment file:

```bash
cp .env.example .env
```

Then start the dev server:

```bash
pnpm dev
```

Open http://localhost:3000. The backend must be running for signup and login to work.

## Environment variables

| Variable      | Required | Description                                                  |
| ------------- | -------- | ------------------------------------------------------------ |
| `BACKEND_URL` | Yes      | Base URL of the FastAPI backend.                             |
| `NODE_ENV`    | No       | Set automatically by Next.js.                                |

Variables are validated with `@t3-oss/env-nextjs` in `lib/env.js`. Set `SKIP_ENV_VALIDATION=1` to bypass validation (useful for Docker builds).

## How it works

- **Session** — a single `access_token` cookie holds an RS256 JWT. `server/auth/auth.lib.ts` reads it, **verifies** the signature and expiry with `jose` (public keys fetched from the backend's `/.well-known/jwks.json`) and then fetches `/users/me` for the profile, returning `{ session, user }` or `null`. Layouts and pages call `getSession()` (memoised with React `cache()`). The frontend never holds the signing key.
- **No refresh tokens** — the token is a long-lived JWT (24h). When it expires the user logs in again. `getSession()` returns `null` for an expired or tampered token.
- **Server actions** — `server/auth/auth.actions.ts` and `server/users/users.actions.ts` call the backend with `fetch` and write the JWT into the cookie. Client components invoke them through `next-safe-action`.
- **Auth flows** — `/auth/login`, `/auth/signup`, `/auth/forgot-password`, `/auth/reset-password` and `/auth/verify-email` cover the FastAPI Users flows. After signing up, the account is unverified: an email-verification link is sent and the user logs in afterwards.
- **Protected actions** — `protectedProcedure` in `lib/safe-action.ts` requires a valid session and forwards the token in the `Authorization` header.
- **Guards** — `app/auth/layout.tsx` redirects authenticated users away from the auth pages, while `app/profile/page.tsx` redirects unauthenticated users to `/auth/login`. The root layout shows a resend-verification banner while the email is unverified.

## Scripts

| Command      | Description                |
| ------------ | -------------------------- |
| `pnpm dev`   | Start the dev server       |
| `pnpm build` | Production build           |
| `pnpm start` | Serve the production build |
| `pnpm lint`  | Run ESLint                 |

## UI components

Components under `components/ui/` are generated with [shadcn/ui](https://ui.shadcn.com/) (config in `components.json`). Add more with:

```bash
pnpm dlx shadcn@latest add <component>
```

## Notes for agents

`AGENTS.md` warns that this project uses a Next.js version whose APIs may differ from older training data. Read the bundled guides under `node_modules/next/dist/docs/` before writing Next.js code.
