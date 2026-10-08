import { cookies } from "next/headers";

import { accessTokenCookieOptions, refreshTokenCookieOptions } from "./cookies";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
};

export async function setAuthCookies(tokens: TokenPair) {
  const cookieStore = await cookies();

  cookieStore.set("access_token", tokens.access_token, accessTokenCookieOptions);
  cookieStore.set("refresh_token", tokens.refresh_token, refreshTokenCookieOptions);
}

export async function clearAuthCookies() {
  const cookieStore = await cookies();

  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");
}
