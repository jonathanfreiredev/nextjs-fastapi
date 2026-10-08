import { env } from "@/lib/env";

// Keep these in sync with the backend token TTLs (app/auth/constants.py).
export const ACCESS_TOKEN_MAX_AGE = 15 * 60; // 15 minutes
export const REFRESH_TOKEN_MAX_AGE = 30 * 24 * 60 * 60; // 30 days

const baseCookieOptions = {
  httpOnly: true,
  secure: env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
};

export const accessTokenCookieOptions = {
  ...baseCookieOptions,
  maxAge: ACCESS_TOKEN_MAX_AGE,
};

export const refreshTokenCookieOptions = {
  ...baseCookieOptions,
  maxAge: REFRESH_TOKEN_MAX_AGE,
};
