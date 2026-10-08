# Frontend — Next.js

The web client for the [Next.js + FastAPI Starter](../README.md). It renders the UI, validates forms, and talks to the FastAPI backend through server actions — the browser never sees the JWT directly.

## Tech stack

- **Next.js 16** (App Router) and **React 19**
- **TypeScript**
- **Tailwind CSS 4** with **shadcn/ui** components (base-nova style, Lucide icons)
- **React Hook Form** + **Zod** for forms and validation
- **next-safe-action** for type-safe server actions
- **@t3-oss/env-nextjs** for environment variable validation
- **Motion** for animations, **jwt-decode** for reading the session token
- **pnpm** as the package manager

## Project structure

```
frontend/
├── app/
│   ├── (root)/            # Public shell: home page + header layout
│   ├── auth/              # /auth/login and /auth/signup (redirects when signed in)
│   ├── profile/           # Protected profile page
│   ├── api/logout/        # Route handler that clears the session cookie
│   ├── layout.tsx         # Root layout (fonts, Toaster)
│   └── globals.css        # Tailwind + theme tokens
├── components/
│   ├── auth/              # Login, signup, profile, change-password forms
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

- **Session** — cookies hold two tokens: `access_token` (15 min JWT) and `refresh_token` (30 days). `server/auth/auth.lib.ts` reads the `access_token` cookie and **verifies** its RS256 signature and expiry with `jose`, using the public keys fetched from the backend's `/.well-known/jwks.json`. It returns `{ session, user }` or `null`. Layouts and pages call `getSession()` to render signed-in vs. signed-out state. The frontend never holds the signing key.
- **Token refresh** — `proxy.ts` (the file convention renamed from `middleware.ts` in Next 16) runs before rendering. If the access token is expired and a refresh token is present, it calls the backend `/auth/refresh`, rotates the pair, and updates both the request and response cookies so the current render is already authenticated.
- **Server actions** — `server/auth/auth.actions.ts` and `server/users/users.actions.ts` call the backend with `fetch` and write the JWT into the cookie. Client components invoke them through `next-safe-action`.
- **Protected actions** — `protectedProcedure` in `lib/safe-action.ts` requires a valid session and forwards the token in the `Authorization` header.
- **Guards** — `app/auth/layout.tsx` redirects authenticated users away from login/signup, while `app/profile/page.tsx` redirects unauthenticated users to `/auth/login`.

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
