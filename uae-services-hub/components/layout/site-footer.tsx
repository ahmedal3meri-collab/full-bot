import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { siteConfig } from "@/lib/config/site";

export async function SiteFooter() {
  const t = await getTranslations();
  const year = new Date().getFullYear();

  return (
    <footer className="mt-16 border-t border-border bg-brand-950 text-sand-100">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-4">
        <div>
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-sand-100 text-sm font-bold text-brand-900">
            {siteConfig.logoText}
          </span>
          <p className="mt-3 text-sm text-sand-100/70">{t("common.siteName")}</p>
        </div>
        <div className="flex flex-col gap-2 text-sm text-sand-100/80">
          <Link href="/about" className="hover:text-gold-400">{t("footer.about")}</Link>
          <Link href="/contact" className="hover:text-gold-400">{t("footer.contact")}</Link>
          <Link href="/faq" className="hover:text-gold-400">{t("footer.faq")}</Link>
        </div>
        <div className="flex flex-col gap-2 text-sm text-sand-100/80">
          <Link href="/legal/terms" className="hover:text-gold-400">{t("footer.terms")}</Link>
          <Link href="/legal/privacy" className="hover:text-gold-400">{t("footer.privacy")}</Link>
          <Link href="/legal/refund" className="hover:text-gold-400">{t("footer.refund")}</Link>
        </div>
        <div className="text-sm text-sand-100/60">
          © {year} {t("common.siteName")}. {t("footer.rights")}.
        </div>
      </div>
    </footer>
  );
}
