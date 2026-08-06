"server only";
import { signupFormSchema } from "@/components/auth/signup-form";
import { publicProcedure } from "@/lib/safe-action";
import { cookies } from "next/headers";
import { env } from "@/lib/env";

export const signupAction = publicProcedure
  .inputSchema(signupFormSchema.omit({ confirmPassword: true }))
  .action(async ({ parsedInput }) => {
    const response = await fetch(`${env.BACKEND_URL}/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(parsedInput),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail ?? "Error creating the user");
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
