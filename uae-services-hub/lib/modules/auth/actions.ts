"use server";

import { headers } from "next/headers";
import { prisma } from "@/lib/db/client";
import { hashPassword, verifyPassword } from "@/lib/auth/password";
import { createUserSession, destroyCurrentSession } from "@/lib/auth/session";
import { isRateLimited } from "@/lib/auth/rate-limit";
import { registerSchema, loginSchema } from "./schemas";

type ActionResult = { ok: true } | { ok: false; error: string };

export async function registerAction(input: unknown): Promise<ActionResult> {
  const parsed = registerSchema.safeParse(input);
  if (!parsed.success) {
    return { ok: false, error: parsed.error.issues[0]?.message ?? "بيانات غير صحيحة" };
  }
  const { fullName, email, phone, password, emirateId } = parsed.data;

  if (email) {
    const exists = await prisma.user.findUnique({ where: { email } });
    if (exists) return { ok: false, error: "email_or_phone_taken" };
  }
  if (phone) {
    const exists = await prisma.user.findUnique({ where: { phone } });
    if (exists) return { ok: false, error: "email_or_phone_taken" };
  }

  const role = await prisma.role.findUnique({ where: { code: "REGISTERED_USER" } });
  if (!role) return { ok: false, error: "role_not_seeded" };

  const passwordHash = await hashPassword(password);

  const user = await prisma.user.create({
    data: {
      fullName,
      email: email || undefined,
      phone: phone || undefined,
      passwordHash,
      roleId: role.id,
      emirateId: emirateId || undefined,
      status: "ACTIVE", // TODO(OTP): بانتظار مزود SMS حقيقي، الحساب يُفعَّل مباشرة — راجع REQUIRED_USER_INPUT.md #2
    },
  });

  await prisma.auditLog.create({
    data: { actorId: user.id, action: "user.register", entityType: "User", entityId: user.id },
  });

  await createUserSession(user.id);
  return { ok: true };
}

export async function loginAction(input: unknown): Promise<ActionResult> {
  const parsed = loginSchema.safeParse(input);
  if (!parsed.success) {
    return { ok: false, error: "invalid_credentials" };
  }
  const { identifier, password } = parsed.data;

  const h = await headers();
  const ip = h.get("x-forwarded-for") ?? "unknown";
  if (isRateLimited(`login:${ip}:${identifier}`)) {
    return { ok: false, error: "too_many_attempts" };
  }

  const isEmail = identifier.includes("@");
  const user = await prisma.user.findUnique({
    where: isEmail ? { email: identifier.toLowerCase() } : { phone: identifier },
  });

  if (!user) return { ok: false, error: "invalid_credentials" };
  if (user.status === "BANNED" || user.status === "SUSPENDED") return { ok: false, error: "account_disabled" };

  const valid = await verifyPassword(user.passwordHash, password);
  if (!valid) return { ok: false, error: "invalid_credentials" };

  await createUserSession(user.id);
  await prisma.auditLog.create({
    data: { actorId: user.id, action: "user.login", entityType: "User", entityId: user.id, ip },
  });

  return { ok: true };
}

export async function logoutAction(): Promise<void> {
  await destroyCurrentSession();
}
