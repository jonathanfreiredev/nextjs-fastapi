"use server";

import { returnServerError } from "next-safe-action";

import { env } from "@/lib/env";
import { protectedProcedure } from "@/lib/safe-action";
import { updateUserPasswordSchema, updateUserSchema } from "./users.schemas";

const EMAIL_TAKEN = "That email is already in use.";

export const updateUserAction = protectedProcedure
  .inputSchema(updateUserSchema)
  .action(async ({ parsedInput, ctx }) => {
    const response = await fetch(`${env.BACKEND_URL}/users/me`, {
      method: "PATCH",
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
      const errorData = await response.json().catch(() => ({}));
      const isEmailTaken = errorData.detail === "UPDATE_USER_EMAIL_ALREADY_EXISTS";

      returnServerError({
        code: response.status,
        message: isEmailTaken
          ? EMAIL_TAKEN
          : errorData.detail || "An error occurred while updating user.",
      });
    }

    return { success: true, user: await response.json() };
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
      const errorData = await response.json().catch(() => ({}));

      returnServerError({
        code: response.status,
        message:
          errorData.detail || "An error occurred while updating user password.",
      });
    }

    return { success: true, user: await response.json() };
  });
