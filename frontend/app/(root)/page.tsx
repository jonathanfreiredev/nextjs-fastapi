import { getSession } from "@/server/auth/auth.lib";

export default async function HomePage() {
  const session = await getSession();

  return (
    <div className="flex flex-1 flex-col items-center justify-center">
      <h1 className="text-2xl font-bold">Welcome to the Home Page</h1>
      {session ? (
        <p className="mt-4 text-lg">
          Logged in as: {session.user.name} ({session.user.email})
        </p>
      ) : (
        <p className="mt-4 text-lg">You are not logged in.</p>
      )}
    </div>
  );
}
