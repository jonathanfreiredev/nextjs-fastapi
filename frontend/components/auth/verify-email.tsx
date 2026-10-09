import Link from "next/link";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { FieldDescription } from "../ui/field";

export const VerifyEmail = () => {
  return (
    <Card className="w-full max-w-125">
      <CardHeader className="text-center">
        <CardTitle className="text-xl">Email verification</CardTitle>
        <CardDescription>Check your inbox</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-4">
        <FieldDescription className="text-center">
          We sent you a verification link. Open it to confirm your email — the
          link signs you in automatically.
        </FieldDescription>
        <Link href="/auth/login">
          <Button variant="link">Go to log in</Button>
        </Link>
      </CardContent>
    </Card>
  );
};
