import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { siteConfig } from "@/lib/config/site";
import { getCurrentUser } from "@/lib/auth/session";
import { LocaleSwitcher } from "./locale-switcher";
import { ThemeToggle } from "./theme-toggle";
import { LogoutButton } from "./logout-button";

export async function SiteHeader() {
  const t = await getTranslations();
  const user = await getCurrentUser();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-900 text-sm font-bold text-gold-400">
            {siteConfig.logoText}
          </span>
          <span className="hidden text-lg font-semibold text-brand-900 sm:inline dark:text-sand-100">
            {t("common.siteName")}
          </span>
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium text-foreground/80 md:flex">
          <Link href="/" className="hover:text-brand-700">{t("nav.home")}</Link>
          <Link href="/categories" className="hover:text-brand-700">{t("nav.categories")}</Link>
          <Link href="/providers" className="hover:text-brand-700">{t("nav.forCompanies")}</Link>
        </nav>

        <div className="ms-auto flex items-center gap-2">
          <Link
            href="/listings/new"
            className="hidden rounded-full bg-gold-500 px-4 py-2 text-sm font-semibold text-brand-950 transition hover:bg-gold-400 sm:inline-block"
          >
            {t("nav.postAd")}
          </Link>
          {user ? (
            <>
              <Link
                href="/account"
                className="hidden rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground/80 transition hover:bg-muted sm:inline-block"
              >
                {user.fullName.split(" ")[0]}
              </Link>
              <LogoutButton />
            </>
          ) : (
            <Link
              href="/login"
              className="rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground/80 transition hover:bg-muted"
            >
              {t("common.login")}
            </Link>
          )}
          <LocaleSwitcher />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
