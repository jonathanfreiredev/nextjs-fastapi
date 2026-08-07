"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { toast } from "@/components/ui/toast";
import { z } from "zod";
import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldSet,
} from "../ui/field";
import { Input } from "../ui/input";
import { loginFormSchema } from "@/server/auth/auth.schemas";
import { loginAction } from "@/server/auth/auth.actions";

export const LoginForm = ({
  className,
  ...props
}: React.ComponentProps<"div">) => {
  const router = useRouter();

  const form = useForm<z.infer<typeof loginFormSchema>>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(data: z.infer<typeof loginFormSchema>) {
    const res = await loginAction(data);

    if (res.serverError) {
      toast.add({
        title: "Login failed!",
        description: res.serverError || "An error occurred during login.",
        type: "error",
      });
      return;
    }

    toast.add({
      title: "Logged in successfully!",
      description: "Welcome back!",
      type: "success",
    });

    form.reset();
    router.refresh();
    router.replace("/");
  }

  return (
    <div
      className={cn("flex w-full max-w-125 flex-col gap-6", className)}
      {...props}
    >
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Log in</CardTitle>
          <CardDescription>
            Enter your email and password to log in to your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form id="form-login" onSubmit={form.handleSubmit(onSubmit)}>
            <FieldSet className="mb-5 w-full">
              <FieldGroup>
                <Controller
                  name="email"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="email">Email</FieldLabel>
                      <Input
                        {...field}
                        id="email"
                        type="email"
                        placeholder="joe@example.com"
                        required
                      />
                      <FieldDescription>
                        Choose a unique email for your account.
                      </FieldDescription>

                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />

                <Controller
                  name="password"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="password">Password</FieldLabel>
                      <Input
                        {...field}
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        autoComplete="off"
                        required
                      />
                      <FieldDescription>
                        Must be at least 8 characters long.
                      </FieldDescription>

                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </FieldGroup>
            </FieldSet>

            <Field>
              <Button
                type="submit"
                form="form-login"
                disabled={form.formState.isSubmitting}
              >
                Log in
              </Button>

              <FieldDescription className="text-center">
                Don&apos;t have an account?{" "}
                <Link href="/auth/signup">
                  <Button
                    variant="link"
                    onClick={() => {
                      form.reset();
                    }}
                    disabled={form.formState.isSubmitting}
                  >
                    Sign up
                  </Button>
                </Link>
              </FieldDescription>
            </Field>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
