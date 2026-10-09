"use server";

import { headers } from "next/headers";
import { returnServerError } from "next-safe-action";

import { createClient } from "@/lib/supabase/server";
import { protectedProcedure, publicProcedure } from "@/lib/safe-action";
import {
  forgotPasswordSchema,
  loginFormSchema,
  resetPasswordSchema,
  signupFormSchema,
} from "./auth.schemas";

const LOGIN_ERROR = "Incorrect email or password.";

/** Absolute base URL of the current request, used to build redirect links. */
async function baseUrl(): Promise<string> {
  const headerList = await headers();
  const host =
    headerList.get("x-forwarded-host") ?? headerList.get("host") ?? "localhost:3000";
  const protocol = headerList.get("x-forwarded-proto") ?? "http";
  return `${protocol}://${host}`;
}

export const signupAction = publicProcedure
  .inputSchema(signupFormSchema.omit({ confirmPassword: true }))
  .action(async ({ parsedInput }) => {
    const supabase = await createClient();

    const { error } = await supabase.auth.signUp({
      email: parsedInput.email,
      password: parsedInput.password,
      options: {
        data: { full_name: parsedInput.name },
        emailRedirectTo: `${await baseUrl()}/auth/confirm?next=/`,
      },
    });

    if (error) {
      returnServerError({
        code: error.status ?? 400,
        message: error.message,
      });
    }

    // Supabase sends the verification email on its own.
    return { success: true };
  });

export const loginAction = publicProcedure
  .inputSchema(loginFormSchema)
  .action(async ({ parsedInput }) => {
    const supabase = await createClient();

    const { error } = await supabase.auth.signInWithPassword({
      email: parsedInput.email,
      password: parsedInput.password,
    });

    if (error) {
      returnServerError({ code: error.status ?? 400, message: LOGIN_ERROR });
    }

    return { success: true };
  });

export const logoutAction = publicProcedure.action(async () => {
  const supabase = await createClient();
  await supabase.auth.signOut();

  return { success: true };
});

export const signInWithGoogleAction = publicProcedure.action(async () => {
  const supabase = await createClient();

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: { redirectTo: `${await baseUrl()}/auth/confirm?next=/` },
  });

  if (error) {
    returnServerError({ code: error.status ?? 400, message: error.message });
  }

  // The client navigates to this URL to start the OAuth dance.
  return { url: data.url };
});

export const forgotPasswordAction = publicProcedure
  .inputSchema(forgotPasswordSchema)
  .action(async ({ parsedInput }) => {
    const supabase = await createClient();

    const { error } = await supabase.auth.resetPasswordForEmail(
      parsedInput.email,
      { redirectTo: `${await baseUrl()}/auth/confirm?next=/auth/reset-password` },
    );

    if (error) {
      returnServerError({
        code: error.status ?? 400,
        message: "Could not start the password reset. Please try again.",
      });
    }

    return { success: true };
  });

export const resetPasswordAction = publicProcedure
  .inputSchema(resetPasswordSchema.omit({ confirmPassword: true }))
  .action(async ({ parsedInput }) => {
    const supabase = await createClient();

    const { error } = await supabase.auth.updateUser({
      password: parsedInput.password,
    });

    if (error) {
      returnServerError({
        code: error.status ?? 400,
        message: "This reset link is invalid or has expired.",
      });
    }

    return { success: true };
  });

export const resendVerificationAction = protectedProcedure.action(
  async ({ ctx }) => {
    const supabase = await createClient();

    const { error } = await supabase.auth.resend({
      type: "signup",
      email: ctx.user.email,
      options: { emailRedirectTo: `${await baseUrl()}/auth/confirm?next=/` },
    });

    if (error) {
      returnServerError({
        code: error.status ?? 400,
        message: "Could not resend the verification email. Please try again.",
      });
    }

    return { success: true };
  },
);
