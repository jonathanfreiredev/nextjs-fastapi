import { redirect } from "next/navigation";

export default async function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // const session = await getSession();

  // const isLoggedIn = !!session?.session;

  const isLoggedIn = false;

  if (isLoggedIn) {
    redirect("/");
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center">
      {children}
    </div>
  );
}
