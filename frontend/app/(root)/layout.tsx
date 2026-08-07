import { Header } from "@/components/header";
import { getSession } from "@/server/auth/auth.lib";

export default async function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await getSession();

  return (
    <>
      <Header session={session} />
      {children}
    </>
  );
}
