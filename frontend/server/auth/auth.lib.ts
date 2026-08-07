"use server";
import { cookies } from "next/headers";
import { jwtDecode } from "jwt-decode";

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

export async function getSession() {
  const cookieStore = await cookies();
  const access_token = cookieStore.get("access_token");

  if (!access_token) {
    return null;
  }

  const decodedToken: { sub: string; name: string; exp: number } = jwtDecode(
    access_token.value,
  );
  const currentTime = Math.floor(Date.now() / 1000);

  if (decodedToken.exp < currentTime) {
    return null;
  }

  return {
    session: {
      token: access_token.value,
      expiresAt: new Date(decodedToken.exp * 1000).toISOString(),
    },
    user: {
      email: decodedToken.sub,
      name: decodedToken.name,
    },
  };
}
