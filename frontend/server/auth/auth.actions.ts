"use server";

import { publicProcedure } from "@/lib/safe-action";
import { cookies } from "next/headers";
import { env } from "@/lib/env";
import { returnServerError } from "next-safe-action";
import { loginFormSchema, signupFormSchema } from "./auth.schemas";
import { logout } from "./auth.service";

export const signupAction = publicProcedure
  .inputSchema(signupFormSchema.omit({ confirmPassword: true }))
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        full_name: parsedInput.name,
        email: parsedInput.email,
        password: parsedInput.password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      returnServerError({
        code: response.status,
        message: errorData.detail || "An error occurred during signup.",
      });
    }

    const token = await response.json();

    const cookieStore = await cookies();

    cookieStore.set("access_token", token.access_token, {
      httpOnly: true,
      secure: env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 24,
    });

    return { success: true };
  });

export const loginAction = publicProcedure
  .inputSchema(loginFormSchema)
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(parsedInput),
    });

    if (!response.ok) {
      const errorData = await response.json();
      returnServerError({
        code: response.status,
        message: errorData.detail || "An error occurred during login.",
      });
    }

    const token = await response.json();

    const cookieStore = await cookies();

    cookieStore.set("access_token", token.access_token, {
      httpOnly: true,
      secure: env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 24,
    });

    return { success: true };
  });

export const logoutAction = publicProcedure.action(async () => {
  return await logout();
});
