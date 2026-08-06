"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { buttonVariants } from "../ui/button";

export function SignInOrSignUpButton() {
  const pathname = usePathname();

  const isLoginPage = pathname === "/auth/login";

  return (
    <Link
      href={isLoginPage ? "/auth/signup" : "/auth/login"}
      className={buttonVariants({ variant: "outline", size: "lg" })}
    >
      {isLoginPage ? "Sign up" : "Log in"}
    </Link>
  );
}
