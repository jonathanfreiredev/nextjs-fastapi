"use client";
import { useState } from "react";

import { toast } from "@/components/ui/toast";
import { signInWithGoogleAction } from "@/server/auth/auth.actions";
import { Button } from "../ui/button";

export const GoogleSignInButton = ({
  className,
}: {
  className?: string;
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  return (
    <Button
      type="button"
      variant="outline"
      className={className}
      disabled={isSubmitting}
      onClick={async () => {
        setIsSubmitting(true);
        const res = await signInWithGoogleAction();

        if (res?.serverError) {
          toast.add({
            title: "Google sign-in failed!",
            description: res.serverError.message,
            type: "error",
          });
          setIsSubmitting(false);
          return;
        }

        if (res?.data?.url) {
          window.location.assign(res.data.url);
        }
      }}
    >
      Continue with Google
    </Button>
  );
};
