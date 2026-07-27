import "server-only";
import argon2 from "argon2";

// Argon2id بإعداد قوي — راجع SECURITY.md
export function hashPassword(plain: string): Promise<string> {
  return argon2.hash(plain, {
    type: argon2.argon2id,
    memoryCost: 19456, // 19 MiB — توصية OWASP 2024 لـ Argon2id
    timeCost: 2,
    parallelism: 1,
  });
}

export function verifyPassword(hash: string, plain: string): Promise<boolean> {
  return argon2.verify(hash, plain);
}
