import { NextResponse } from "next/server";
import { prisma } from "@/lib/db/client";

export async function GET() {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return NextResponse.json({ status: "ok", db: "up", timestamp: new Date().toISOString() });
  } catch {
    return NextResponse.json({ status: "error", db: "down" }, { status: 503 });
  }
}

export const dynamic = "force-dynamic";
