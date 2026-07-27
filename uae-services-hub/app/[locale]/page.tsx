import { getLocale, getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { prisma } from "@/lib/db/client";
import { getTopLevelCategories } from "@/lib/modules/categories/queries";
import { getFeaturedListings } from "@/lib/modules/listings/queries";
import { getVerifiedCompanies } from "@/lib/modules/companies/queries";
import { CategoryCard } from "@/components/categories/category-card";
import { ListingCard } from "@/components/listings/listing-card";
import { CompanyCard } from "@/components/companies/company-card";
import { HeroSearch } from "@/components/home/hero-search";
import { MessagesSquare, ClipboardList, Star, ArrowRight, ArrowLeft } from "lucide-react";

export default async function HomePage() {
  const locale = await getLocale();
  const t = await getTranslations();
  const isAr = locale === "ar";
  const ArrowIcon = isAr ? ArrowLeft : ArrowRight;

  const [categories, featuredListings, companies, emirates] = await Promise.all([
    getTopLevelCategories(),
    getFeaturedListings(8),
    getVerifiedCompanies(6),
    prisma.emirate.findMany({ orderBy: { sortOrder: "asc" } }),
  ]);

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-brand-950">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "radial-gradient(circle at 20% 20%, #b8925a 0, transparent 45%), radial-gradient(circle at 80% 60%, #4c6339 0, transparent 45%)" }} />
        <div className="relative mx-auto max-w-5xl px-4 py-20 text-center sm:px-6">
          <h1 className="text-3xl font-bold text-sand-100 sm:text-5xl">{t("home.heroTitle")}</h1>
          <p className="mx-auto mt-4 max-w-2xl text-balance text-sand-100/75 sm:text-lg">{t("home.heroSubtitle")}</p>
          <div className="mx-auto mt-8 max-w-2xl">
            <HeroSearch emirates={emirates} locale={locale} />
          </div>
        </div>
      </section>

      {/* الأقسام */}
      <section className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
        <h2 className="mb-6 text-xl font-bold text-foreground sm:text-2xl">{t("home.sectionsTitle")}</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {categories.map((c) => (
            <CategoryCard key={c.id} category={c} />
          ))}
        </div>
      </section>

      {/* إعلانات مميزة */}
      <section className="bg-muted/40 py-14">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-bold text-foreground sm:text-2xl">{t("home.featuredTitle")}</h2>
            <Link href="/search" className="flex items-center gap-1 text-sm font-medium text-brand-700 hover:underline dark:text-gold-400">
              {t("home.viewAll")} <ArrowIcon className="h-4 w-4" />
            </Link>
          </div>
          {featuredListings.length === 0 ? (
            <p className="text-sm text-muted-foreground">{t("home.featuredEmpty")}</p>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {featuredListings.map((l) => (
                <ListingCard key={l.id} listing={l} />
              ))}
            </div>
          )}
          <p className="mt-6 text-xs text-muted-foreground">{t("home.demoDataNotice")}</p>
        </div>
      </section>

      {/* شركات موثقة */}
      {companies.length > 0 && (
        <section className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
          <h2 className="mb-6 text-xl font-bold text-foreground sm:text-2xl">{t("home.companiesTitle")}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {companies.map((c) => (
              <CompanyCard key={c.id} company={c} />
            ))}
          </div>
        </section>
      )}

      {/* كيف تعمل المنصة */}
      <section className="bg-brand-900 py-14">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <h2 className="mb-8 text-center text-xl font-bold text-sand-100 sm:text-2xl">{t("home.howItWorksTitle")}</h2>
          <div className="grid gap-6 sm:grid-cols-3">
            {[
              { icon: ClipboardList, title: t("home.howItWorks1Title"), body: t("home.howItWorks1Body") },
              { icon: MessagesSquare, title: t("home.howItWorks2Title"), body: t("home.howItWorks2Body") },
              { icon: Star, title: t("home.howItWorks3Title"), body: t("home.howItWorks3Body") },
            ].map((step, i) => (
              <div key={i} className="rounded-xl border border-white/10 bg-white/5 p-6 text-center">
                <span className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-full bg-gold-500 text-brand-950">
                  <step.icon className="h-6 w-6" />
                </span>
                <p className="font-semibold text-sand-100">{step.title}</p>
                <p className="mt-2 text-sm text-sand-100/70">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* دعوة الشركات */}
      <section className="mx-auto max-w-4xl px-4 py-16 text-center sm:px-6">
        <h2 className="text-xl font-bold text-foreground sm:text-2xl">{t("home.providersCtaTitle")}</h2>
        <p className="mx-auto mt-3 max-w-xl text-muted-foreground">{t("home.providersCtaBody")}</p>
        <Link
          href="/providers/register"
          className="mt-6 inline-flex rounded-full bg-gold-500 px-8 py-3 text-sm font-semibold text-brand-950 transition hover:bg-gold-400"
        >
          {t("home.providersCtaButton")}
        </Link>
      </section>
    </div>
  );
}

export const dynamic = "force-dynamic";
