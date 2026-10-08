"use server";

import { publicProcedure } from "@/lib/safe-action";
import { env } from "@/lib/env";
import { returnServerError } from "next-safe-action";
import { loginFormSchema, signupFormSchema } from "./auth.schemas";
import { setAuthCookies } from "./session";
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

    await setAuthCookies(await response.json());

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

    await setAuthCookies(await response.json());

    return { success: true };
  });

export const logoutAction = publicProcedure.action(async () => {
  return await logout();
});
