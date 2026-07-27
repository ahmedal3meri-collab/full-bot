"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { Search } from "lucide-react";

type Emirate = { id: string; slug: string; nameAr: string; nameEn: string };

export function HeroSearch({ emirates, locale }: { emirates: Emirate[]; locale: string }) {
  const t = useTranslations("common");
  const router = useRouter();
  const [q, setQ] = useState("");
  const [emirate, setEmirate] = useState("");

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (emirate) params.set("emirate", emirate);
    router.push(`/search?${params.toString()}`);
  }

  return (
    <form
      onSubmit={onSubmit}
      className="flex w-full flex-col gap-2 rounded-2xl border border-border bg-card p-2 shadow-xl shadow-brand-950/10 sm:flex-row"
    >
      <select
        value={emirate}
        onChange={(e) => setEmirate(e.target.value)}
        className="rounded-xl border border-border bg-background px-3 py-3 text-sm text-foreground sm:w-48"
      >
        <option value="">{t("allEmirates")}</option>
        {emirates.map((e) => (
          <option key={e.id} value={e.slug}>
            {locale === "ar" ? e.nameAr : e.nameEn}
          </option>
        ))}
      </select>
      <input
        type="text"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={t("search")}
        className="flex-1 rounded-xl border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />
      <button
        type="submit"
        className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-900 px-6 py-3 text-sm font-semibold text-gold-400 transition hover:bg-brand-800"
      >
        <Search className="h-4 w-4" />
      </button>
    </form>
  );
}
