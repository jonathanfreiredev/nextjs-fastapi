import { cache } from "react";
import { cookies } from "next/headers";
import { createRemoteJWKSet, jwtVerify } from "jose";

import { env } from "@/lib/env";

export type Session = {
  session: {
    token: string;
    expiresAt: string;
  };
  user: {
    id: string;
    email: string;
    name: string;
    isVerified: boolean;
  };
};

// Public keys fetched from the backend's JWKS endpoint and cached by jose. The
// frontend verifies the RS256 signature with the public key only; it never holds
// the signing key.
const jwks = createRemoteJWKSet(new URL("/.well-known/jwks.json", env.BACKEND_URL));

export const getSession = cache(async (): Promise<Session | null> => {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    return null;
  }

  let expiresAt: string;
  try {
    const { payload } = await jwtVerify(accessToken, jwks, {
      algorithms: ["RS256"],
      audience: "fastapi-users:auth",
    });
    expiresAt = new Date((payload.exp as number) * 1000).toISOString();
  } catch {
    // Malformed, tampered or expired token.
    return null;
  }

  // The token only carries the user id, so the profile is fetched from the API.
  const response = await fetch(`${env.BACKEND_URL}/users/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });

  if (!response.ok) {
    return null;
  }

  const user = await response.json();

  return {
    session: { token: accessToken, expiresAt },
    user: {
      id: user.id,
      email: user.email,
      name: user.full_name ?? "",
      isVerified: user.is_verified,
    },
  };
});
