"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { toast } from "@/components/ui/toast";
import { z } from "zod";
import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldSet,
} from "../ui/field";
import { Input } from "../ui/input";

const formSchema = z.object({
  currentPassword: z
    .string()
    .min(8, { message: "Current password must be at least 8 characters" }),
  newPassword: z
    .string()
    .min(8, { message: "Password must be at least 8 characters" }),
  confirmPassword: z
    .string()
    .min(8, { message: "Confirm Password must be at least 8 characters" }),
});

export const ChangePasswordForm = ({
  className,
  ...props
}: React.ComponentProps<"div">) => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    },
  });

  async function onSubmit(data: z.infer<typeof formSchema>) {
    const { confirmPassword, ...resetData } = data;

    if (data.newPassword !== data.confirmPassword) {
      toast.add({
        title: "Passwords do not match!",
        description: "Please make sure your passwords match.",
        type: "error",
      });
      return;
    }

    // await authClient.changePassword({
    //   ...resetData,
    //   revokeOtherSessions: true,
    //   fetchOptions: {
    //     async onSuccess() {
    //       form.reset();
    //       toast.success("Password changed successfully!", {
    //         position: "bottom-right",
    //       });
    //       window.location.reload();
    //     },
    //     onError(error) {
    //       toast.error("Failed to change password!", {
    //         description: error.error.message,
    //         position: "bottom-right",
    //       });
    //     },
    //   },
    // });
  }

  return (
    <div
      className={cn("flex w-full max-w-125 flex-col gap-6", className)}
      {...props}
    >
      <form id="form-change-password" onSubmit={form.handleSubmit(onSubmit)}>
        <FieldSet className="mb-5 w-full">
          <FieldGroup>
            <Field>
              <Controller
                name="currentPassword"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="currentPassword">
                      Current Password
                    </FieldLabel>
                    <Input
                      {...field}
                      id="currentPassword"
                      type="password"
                      placeholder="••••••••"
                      autoComplete="current-password"
                      required
                    />

                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
            </Field>
            <Field>
              <Field className="grid grid-cols-2 gap-4">
                <Controller
                  name="newPassword"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="newPassword">
                        New Password
                      </FieldLabel>
                      <Input
                        {...field}
                        id="newPassword"
                        type="password"
                        placeholder="••••••••"
                        autoComplete="off"
                        required
                      />

                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
                <Controller
                  name="confirmPassword"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="confirmPassword">
                        Confirm Password
                      </FieldLabel>
                      <Input
                        {...field}
                        id="confirmPassword"
                        type="password"
                        placeholder="••••••••"
                        autoComplete="off"
                        required
                      />

                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </Field>
              <FieldDescription>
                Must be at least 8 characters long.
              </FieldDescription>
            </Field>
          </FieldGroup>
        </FieldSet>

        <Field>
          <Button
            type="submit"
            form="form-change-password"
            disabled={form.formState.isSubmitting}
          >
            Change Password
          </Button>
        </Field>
      </form>
    </div>
  );
};
