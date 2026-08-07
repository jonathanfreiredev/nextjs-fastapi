import { logout } from "@/server/auth/auth.service";

export async function GET() {
  await logout();

  return Response.json({ message: "Logged out successfully" });
}
