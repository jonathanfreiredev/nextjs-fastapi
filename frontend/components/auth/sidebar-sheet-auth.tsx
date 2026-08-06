"use client";
import { LogInIcon, LogOutIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Item, ItemContent, ItemMedia, ItemTitle } from "../ui/item";
import Link from "next/link";
import { SheetClose } from "../ui/sheet";

export function SidebarSheetAuth() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  // const { data, isPending } = authClient.useSession();

  // if (isPending) return null;

  // const isLoggedIn = !!data?.session;

  const isLoggedIn = true;

  return (
    <>
      {!isLoggedIn ? (
        <SheetClose
          render={
            <Item
              variant="default"
              size="sm"
              className="cursor-pointer"
              render={
                <Link href="/auth/login">
                  <ItemMedia>
                    <LogInIcon className="size-5" />
                  </ItemMedia>
                  <ItemContent>
                    <ItemTitle>Log in</ItemTitle>
                  </ItemContent>
                </Link>
              }
            />
          }
        />
      ) : (
        <SheetClose
          render={
            <Item
              variant="muted"
              size="sm"
              className="cursor-pointer bg-red-50"
              onClick={async () => {
                if (isSubmitting) return;

                setIsSubmitting(true);
                // await authClient.signOut();
                router.refresh();
                setIsSubmitting(false);
              }}
            >
              <ItemMedia>
                <LogOutIcon className="size-5" />
              </ItemMedia>
              <ItemContent>
                <ItemTitle>Sign out</ItemTitle>
              </ItemContent>
            </Item>
          }
        />
      )}
    </>
  );
}
