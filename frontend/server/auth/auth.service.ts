"use server";

import { cookies } from "next/headers";

import { env } from "@/lib/env";
import { clearAuthCookies } from "./session";

export const logout = async () => {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get("refresh_token")?.value;

  if (refreshToken) {
    try {
      await fetch(`${env.BACKEND_URL}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // Clear the local session even if the backend is unreachable.
    }
  }

  await clearAuthCookies();

  return { success: true };
};
