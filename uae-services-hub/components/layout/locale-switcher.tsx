"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";

export function LocaleSwitcher() {
  const locale = useLocale();
  const t = useTranslations("common");
  const pathname = usePathname();
  const router = useRouter();

  function switchLocale() {
    const next = locale === "ar" ? "en" : "ar";
    router.replace(pathname, { locale: next });
  }

  return (
    <button
      type="button"
      onClick={switchLocale}
      className="rounded-full border border-border px-3 py-1.5 text-sm font-medium text-foreground/80 transition hover:bg-muted"
    >
      {t("language")}
    </button>
  );
}
