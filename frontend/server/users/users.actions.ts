"use server";
import { protectedProcedure } from "@/lib/safe-action";
import { updateUserSchema, updateUserPasswordSchema } from "./users.schemas";
import { env } from "@/lib/env";
import { returnServerError } from "next-safe-action";
import { cookies } from "next/headers";

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

    const resUpdateToken = await fetch(`${env.BACKEND_URL}/auth/update-token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ctx.session.token}`,
      },
    });

    if (!resUpdateToken.ok) {
      const errorData = await resUpdateToken.json();
      returnServerError({
        code: resUpdateToken.status,
        message:
          errorData.detail || "An error occurred while updating the token.",
      });
    }

    const newToken = await resUpdateToken.json();

    const cookieStore = await cookies();

    cookieStore.set("access_token", newToken.access_token, {
      httpOnly: true,
      secure: env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 24,
    });

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
