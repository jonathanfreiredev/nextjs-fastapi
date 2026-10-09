import { env } from "@/lib/env";

// Keep in sync with ACCESS_TOKEN_LIFETIME_SECONDS (backend/app/auth/constants.py).
export const ACCESS_TOKEN_MAX_AGE = 60 * 60 * 24; // 24 hours

export const accessTokenCookieOptions = {
  httpOnly: true,
  secure: env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: ACCESS_TOKEN_MAX_AGE,
};
