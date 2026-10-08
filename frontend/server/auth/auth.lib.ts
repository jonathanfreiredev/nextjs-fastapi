"use server";
import { cookies } from "next/headers";
import { createRemoteJWKSet, jwtVerify } from "jose";
import { env } from "@/lib/env";

export type Session = {
  session: {
    token: string;
    expiresAt: string;
  };
  user: {
    email: string;
    name: string;
  };
};

// The public key is fetched from the backend's JWKS endpoint and cached by jose.
const jwks = createRemoteJWKSet(new URL("/.well-known/jwks.json", env.BACKEND_URL));

export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies();
  const access_token = cookieStore.get("access_token");

  if (!access_token) {
    return null;
  }

  try {
    // Verifies the RS256 signature and the expiry; the frontend only holds the public key.
    const { payload } = await jwtVerify(access_token.value, jwks, {
      algorithms: ["RS256"],
    });

    return {
      session: {
        token: access_token.value,
        expiresAt: new Date((payload.exp as number) * 1000).toISOString(),
      },
      user: {
        email: payload.sub as string,
        name: payload.name as string,
      },
    };
  } catch {
    // Malformed, tampered or expired token.
    return null;
  }
}
