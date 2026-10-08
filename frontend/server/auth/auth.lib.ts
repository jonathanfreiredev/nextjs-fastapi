"use server";
import { cookies } from "next/headers";
import { jwtVerify } from "jose";
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

const secret = new TextEncoder().encode(env.JWT_SECRET);

export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies();
  const access_token = cookieStore.get("access_token");

  if (!access_token) {
    return null;
  }

  try {
    // Verifies the signature and the expiry; decoding alone would trust a forged cookie.
    const { payload } = await jwtVerify(access_token.value, secret, {
      algorithms: ["HS256"],
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
