"use client";

import { useState, useTransition } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { loginAction } from "@/lib/modules/auth/actions";

export function LoginForm() {
  const t = useTranslations("auth");
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ identifier: "", password: "" });

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    startTransition(async () => {
      const result = await loginAction(form);
      if (result.ok) {
        router.push("/");
        router.refresh();
      } else {
        setError(result.error === "invalid_credentials" ? t("invalidCredentials") : result.error);
      }
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {error && <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>}
      <label className="block">
        <span className="mb-1 block text-sm font-medium text-foreground/80">{t("email")} / {t("phone")}</span>
        <input
          required
          value={form.identifier}
          onChange={(e) => setForm({ ...form, identifier: e.target.value })}
          className="input"
        />
      </label>
      <label className="block">
        <span className="mb-1 block text-sm font-medium text-foreground/80">{t("password")}</span>
        <input
          type="password"
          required
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          className="input"
        />
      </label>
      <button type="submit" disabled={isPending} className="btn-primary w-full">
        {isPending ? "..." : t("submitLogin")}
      </button>
    </form>
  );
}
