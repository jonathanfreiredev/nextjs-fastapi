"use server";
import { protectedProcedure } from "@/lib/safe-action";
import { updateUserSchema, updateUserPasswordSchema } from "./users.schemas";
import { env } from "@/lib/env";
import { returnServerError } from "next-safe-action";
import { cookies } from "next/headers";
import { setAuthCookies } from "@/server/auth/session";

export const updateUserAction = protectedProcedure
  .inputSchema(updateUserSchema)
  .action(async ({ parsedInput, ctx }) => {
    const response = await fetch(`${env.BACKEND_URL}/users/me/`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ctx.session.token}`,
      },
      body: JSON.stringify({
        full_name: parsedInput.name,
        email: parsedInput.email,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();

      returnServerError({
        code: response.status,
        message: errorData.detail || "An error occurred while updating user.",
      });
    }

    const updatedUser = await response.json();

    // Changing the email invalidates the current access token (its `sub` is the
    // old email), so exchange the refresh token for a fresh pair.
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get("refresh_token")?.value;

    if (!refreshToken) {
      returnServerError({
        code: 401,
        message: "Your session has expired. Please log in again.",
      });
    }

    const refreshResponse = await fetch(`${env.BACKEND_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!refreshResponse.ok) {
      const errorData = await refreshResponse.json();
      returnServerError({
        code: refreshResponse.status,
        message: errorData.detail || "An error occurred while refreshing the session.",
      });
    }

    await setAuthCookies(await refreshResponse.json());

    return { success: true, user: updatedUser };
  });

export const updateUserPasswordAction = protectedProcedure
  .inputSchema(updateUserPasswordSchema.omit({ confirmNewPassword: true }))
  .action(async ({ parsedInput, ctx }) => {
    const response = await fetch(`${env.BACKEND_URL}/users/me/password/`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ctx.session.token}`,
      },
      body: JSON.stringify({
        old_password: parsedInput.currentPassword,
        new_password: parsedInput.newPassword,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      returnServerError({
        code: response.status,
        message:
          errorData.detail || "An error occurred while updating user password.",
      });
    }

    const updatedUser = await response.json();

    return { success: true, user: updatedUser };
  });