"use server";

import { clearAuthCookies } from "./session";

export const logout = async () => {
  // A JWT cannot be invalidated server-side; clearing the cookie ends the session.
  await clearAuthCookies();

  return { success: true };
};
