import "server-only";

// حماية أولية لتسجيل الدخول: عداد في الذاكرة (per-process). هذا حل مؤقت فقط —
// الإنتاج يحتاج Redis (الخدمة موجودة بـ docker-compose لكن غير مربوطة بعد بطبقة auth)، راجع progress/phase-1.md.
const attempts = new Map<string, { count: number; resetAt: number }>();

const WINDOW_MS = 15 * 60 * 1000;
const MAX_ATTEMPTS = 10;

export function isRateLimited(key: string): boolean {
  const now = Date.now();
  const entry = attempts.get(key);
  if (!entry || entry.resetAt < now) {
    attempts.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return false;
  }
  entry.count += 1;
  return entry.count > MAX_ATTEMPTS;
}
