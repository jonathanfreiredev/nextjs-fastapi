import { cookies } from "next/headers";

import { accessTokenCookieOptions } from "./cookies";

export async function setAuthCookie(accessToken: string) {
  const cookieStore = await cookies();

  cookieStore.set("access_token", accessToken, accessTokenCookieOptions);
}

export async function clearAuthCookies() {
  const cookieStore = await cookies();

  cookieStore.delete("access_token");
}
