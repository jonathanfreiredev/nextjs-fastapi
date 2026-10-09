import { cache } from "react";

import { env } from "@/lib/env";
import { createClient } from "@/lib/supabase/server";

export type Session = {
  session: {
    token: string;
    expiresAt: string | null;
  };
  user: {
    id: string;
    email: string;
    name: string;
    isVerified: boolean;
  };
};

/**
 * Resolve the current session. The Supabase client validates the access token
 * (and refreshes it if needed); the domain profile is fetched from the backend,
 * which provisions it on first use.
 */
export const getSession = cache(async (): Promise<Session | null> => {
  const supabase = await createClient();

  const { data: userData, error } = await supabase.auth.getUser();
  if (error || !userData.user) {
    return null;
  }

  const user = userData.user;
  const { data: sessionData } = await supabase.auth.getSession();
  const token = sessionData.session?.access_token ?? "";
  const expiresAt = sessionData.session?.expires_at
    ? new Date(sessionData.session.expires_at * 1000).toISOString()
    : null;

  let name = (user.user_metadata?.full_name as string | undefined) ?? "";
  if (token) {
    const response = await fetch(`${env.BACKEND_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (response.ok) {
      const profile = await response.json();
      name = profile.full_name ?? name;
    }
  }

  return {
    session: { token, expiresAt },
    user: {
      id: user.id,
      email: user.email ?? "",
      name,
      isVerified: Boolean(user.email_confirmed_at || user.confirmed_at),
    },
  };
});
