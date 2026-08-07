import { logout } from "@/server/auth/auth.service";
import { revalidatePath } from "next/cache";

export async function GET() {
  await logout();

  revalidatePath("/");

  return Response.json({ message: "Logged out successfully" });
}
