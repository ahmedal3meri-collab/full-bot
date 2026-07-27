// Worker — عملية خلفية منفصلة عن web
// الحالة الفعلية: تنفيذ حقيقي واحد فقط (إنهاء صلاحية الإعلانات المنتهية) —
// بقية مهام المرحلة 3 (إشعارات، فهرسة RAG) غير مبنية بعد، راجع IMPLEMENTATION_PLAN.md.
// لا تدّعِ اكتمال BullMQ الكامل قبل بنائه فعليًا.

import { PrismaClient } from "@prisma/client";
import Redis from "ioredis";

const prisma = new PrismaClient();
const redis = new Redis(process.env.REDIS_URL ?? "redis://localhost:6379");

const SWEEP_INTERVAL_MS = 60_000;

async function expireOldListings() {
  const result = await prisma.listing.updateMany({
    where: { status: "PUBLISHED", expiresAt: { lt: new Date() } },
    data: { status: "EXPIRED" },
  });
  if (result.count > 0) {
    console.log(`[worker] expired ${result.count} listing(s)`);
  }
}

async function main() {
  await redis.ping();
  console.log("[worker] connected to Redis");
  await prisma.$queryRaw`SELECT 1`;
  console.log("[worker] connected to PostgreSQL");
  console.log("[worker] started — sweeping expired listings every", SWEEP_INTERVAL_MS / 1000, "s");

  await expireOldListings();
  setInterval(() => {
    expireOldListings().catch((err) => console.error("[worker] sweep failed", err));
  }, SWEEP_INTERVAL_MS);
}

main().catch((err) => {
  console.error("[worker] fatal error", err);
  process.exit(1);
});

process.on("SIGTERM", async () => {
  await prisma.$disconnect();
  redis.disconnect();
  process.exit(0);
});
