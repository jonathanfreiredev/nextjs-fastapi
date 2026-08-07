"use server";
import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";

export const logout = async () => {
  const cookieStore = await cookies();

  cookieStore.delete("access_token");

  revalidatePath("/");

  return { success: true };
};
