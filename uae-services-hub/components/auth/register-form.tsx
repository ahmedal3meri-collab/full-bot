"use client";

import { useState, useTransition } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { registerAction } from "@/lib/modules/auth/actions";

type Emirate = { id: string; slug: string; nameAr: string; nameEn: string };

export function RegisterForm({ emirates, locale }: { emirates: Emirate[]; locale: string }) {
  const t = useTranslations("auth");
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ fullName: "", email: "", phone: "", password: "", emirateId: "" });

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    startTransition(async () => {
      const result = await registerAction(form);
      if (result.ok) {
        router.push("/");
        router.refresh();
      } else {
        setError(result.error === "email_or_phone_taken" ? t("emailOrPhoneTaken") : result.error);
      }
    });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {error && <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>}
      <Field label={t("fullName")}>
        <input
          required
          value={form.fullName}
          onChange={(e) => setForm({ ...form, fullName: e.target.value })}
          className="input"
        />
      </Field>
      <Field label={t("email")}>
        <input
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="input"
        />
      </Field>
      <Field label={t("phone")}>
        <input
          type="tel"
          placeholder="+9715xxxxxxxx"
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
          className="input"
        />
      </Field>
      <Field label={t("password")}>
        <input
          type="password"
          required
          minLength={8}
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          className="input"
        />
      </Field>
      <Field label={t("emirate")}>
        <select
          value={form.emirateId}
          onChange={(e) => setForm({ ...form, emirateId: e.target.value })}
          className="input"
        >
          <option value="">—</option>
          {emirates.map((e) => (
            <option key={e.id} value={e.id}>
              {locale === "ar" ? e.nameAr : e.nameEn}
            </option>
          ))}
        </select>
      </Field>
      <button type="submit" disabled={isPending} className="btn-primary w-full">
        {isPending ? "..." : t("submitRegister")}
      </button>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-foreground/80">{label}</span>
      {children}
    </label>
  );
}
