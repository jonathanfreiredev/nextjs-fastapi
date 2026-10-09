"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { FieldDescription } from "../ui/field";
import { verifyEmailAction } from "@/server/auth/auth.actions";

type Status = "loading" | "success" | "error";

export const VerifyEmail = ({ token }: { token: string }) => {
  const [status, setStatus] = useState<Status>("loading");
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    verifyEmailAction({ token })
      .then((res) => setStatus(res?.serverError ? "error" : "success"))
      .catch(() => setStatus("error"));
  }, [token]);

  return (
    <Card className="w-full max-w-125">
      <CardHeader className="text-center">
        <CardTitle className="text-xl">Email verification</CardTitle>
        <CardDescription>
          {status === "loading" && "Verifying your email..."}
          {status === "success" && "Your email is now verified."}
          {status === "error" && "We could not verify your email."}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-4">
        {status !== "loading" && (
          <FieldDescription className="text-center">
            {status === "success"
              ? "You can now log in to your account."
              : "The link may be invalid or already used. Request a new one from your account."}
          </FieldDescription>
        )}
        <Link href="/auth/login">
          <Button variant="link">Go to log in</Button>
        </Link>
      </CardContent>
    </Card>
  );
};
