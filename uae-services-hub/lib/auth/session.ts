import "server-only";
import { cookies, headers } from "next/headers";
import { randomBytes, createHash } from "node:crypto";
import { prisma } from "@/lib/db/client";

const SESSION_COOKIE = "ush_session";
const SESSION_TTL_DAYS = 30;

function hashToken(token: string): string {
  return createHash("sha256").update(token).digest("hex");
}

export async function createUserSession(userId: string) {
  const token = randomBytes(32).toString("hex");
  const tokenHash = hashToken(token);
  const expiresAt = new Date(Date.now() + SESSION_TTL_DAYS * 24 * 60 * 60 * 1000);

  const h = await headers();
  await prisma.session.create({
    data: {
      userId,
      tokenHash,
      expiresAt,
      userAgent: h.get("user-agent") ?? undefined,
      ip: h.get("x-forwarded-for") ?? undefined,
    },
  });

  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    expires: expiresAt,
  });
}

export async function getCurrentUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (!token) return null;

  const tokenHash = hashToken(token);
  const session = await prisma.session.findUnique({
    where: { tokenHash },
    include: { user: { include: { role: { include: { permissions: { include: { permission: true } } } } } } },
  });

  if (!session || session.revokedAt || session.expiresAt < new Date()) {
    return null;
  }

  return session.user;
}

// إلغاء فوري للجلسة الحالية — يدعم أيضًا إلغاء أي جلسة أخرى عبر id (لوحة "الأجهزة النشطة" لاحقًا)
export async function destroyCurrentSession() {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (token) {
    const tokenHash = hashToken(token);
    await prisma.session.updateMany({ where: { tokenHash }, data: { revokedAt: new Date() } });
  }
  cookieStore.delete(SESSION_COOKIE);
}

export async function revokeAllSessionsForUser(userId: string) {
  await prisma.session.updateMany({ where: { userId, revokedAt: null }, data: { revokedAt: new Date() } });
}
