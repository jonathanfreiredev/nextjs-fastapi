import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

import { env } from "@/lib/env";
import { accessTokenCookieOptions, refreshTokenCookieOptions } from "@/server/auth/cookies";

const secret = new TextEncoder().encode(env.JWT_SECRET);

async function isAccessTokenValid(token: string | undefined): Promise<boolean> {
  if (!token) {
    return false;
  }

  try {
    await jwtVerify(token, secret, { algorithms: ["HS256"] });
    return true;
  } catch {
    return false;
  }
}

export async function proxy(request: NextRequest) {
  const accessToken = request.cookies.get("access_token")?.value;
  const refreshToken = request.cookies.get("refresh_token")?.value;

  // Nothing to do when the access token is still valid or there is nothing to refresh with.
  if ((await isAccessTokenValid(accessToken)) || !refreshToken) {
    return NextResponse.next();
  }

  const response = await fetch(`${env.BACKEND_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    return NextResponse.next();
  }

  const tokens = await response.json();

  // Update the request cookies so the current render sees the new tokens,
  // and the response cookies so the browser stores them for the next request.
  request.cookies.set("access_token", tokens.access_token);
  request.cookies.set("refresh_token", tokens.refresh_token);

  const nextResponse = NextResponse.next({ request });
  nextResponse.cookies.set("access_token", tokens.access_token, accessTokenCookieOptions);
  nextResponse.cookies.set("refresh_token", tokens.refresh_token, refreshTokenCookieOptions);

  return nextResponse;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$).*)"],
};
