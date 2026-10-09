"use server";

import { returnServerError } from "next-safe-action";
import { z } from "zod";

import { env } from "@/lib/env";
import { protectedProcedure, publicProcedure } from "@/lib/safe-action";
import {
  forgotPasswordSchema,
  loginFormSchema,
  resetPasswordSchema,
  signupFormSchema,
} from "./auth.schemas";
import { clearAuthCookies, setAuthCookie } from "./session";

const REGISTER_ERROR = "An account with this email already exists.";
const LOGIN_ERROR = "Incorrect email or password.";

async function backendError(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => null);
  const detail = body?.detail;
  return typeof detail === "string" ? detail : fallback;
}

export const signupAction = publicProcedure
  .inputSchema(signupFormSchema.omit({ confirmPassword: true }))
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: parsedInput.name,
        email: parsedInput.email,
        password: parsedInput.password,
      }),
    });

    if (!response.ok) {
      returnServerError({
        code: response.status,
        message: await backendError(response, REGISTER_ERROR),
      });
    }

    // The account is created unverified and a verification email is sent.
    return { success: true };
  });

export const loginAction = publicProcedure
  .inputSchema(loginFormSchema)
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/jwt/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: parsedInput.email,
        password: parsedInput.password,
      }),
    });

    if (!response.ok) {
      returnServerError({ code: response.status, message: LOGIN_ERROR });
    }

    const { access_token } = await response.json();
    await setAuthCookie(access_token);

    return { success: true };
  });

export const logoutAction = publicProcedure.action(async () => {
  await clearAuthCookies();

  return { success: true };
});

export const forgotPasswordAction = publicProcedure
  .inputSchema(forgotPasswordSchema)
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: parsedInput.email }),
    });

    if (!response.ok) {
      returnServerError({
        code: response.status,
        message: "Could not start the password reset. Please try again.",
      });
    }

    return { success: true };
  });

export const resetPasswordAction = publicProcedure
  .inputSchema(resetPasswordSchema)
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: parsedInput.token,
        password: parsedInput.password,
      }),
    });

    if (!response.ok) {
      returnServerError({
        code: response.status,
        message: "This reset link is invalid or has expired.",
      });
    }

    return { success: true };
  });

export const verifyEmailAction = publicProcedure
  .inputSchema(z.object({ token: z.string().min(1) }))
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: parsedInput.token }),
    });

    if (!response.ok) {
      returnServerError({
        code: response.status,
        message: "This verification link is invalid or has already been used.",
      });
    }

    return { success: true };
  });

export const resendVerificationAction = protectedProcedure.action(async ({ ctx }) => {
  const response = await fetch(`${env.BACKEND_URL}/auth/request-verify-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: ctx.user.email }),
  });

  if (!response.ok) {
    returnServerError({
      code: response.status,
      message: "Could not resend the verification email. Please try again.",
    });
  }

  return { success: true };
});
