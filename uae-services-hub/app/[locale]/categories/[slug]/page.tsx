import { notFound } from "next/navigation";
import { getLocale, getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { getCategoryBySlug } from "@/lib/modules/categories/queries";
import { getListingsByCategorySlug } from "@/lib/modules/listings/queries";
import { CategoryIcon } from "@/lib/modules/categories/icons";
import { ListingCard } from "@/components/listings/listing-card";
import { prisma } from "@/lib/db/client";

export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ emirate?: string; page?: string }>;
}) {
  const { slug } = await params;
  const { emirate, page } = await searchParams;
  const locale = await getLocale();
  const isAr = locale === "ar";
  const t = await getTranslations("home");

  const category = await getCategoryBySlug(slug);
  if (!category) notFound();

  const isParent = category.children.length > 0;
  const emirates = await prisma.emirate.findMany({ orderBy: { sortOrder: "asc" } });

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <div className="mb-8 flex items-center gap-3">
        <span className="grid h-12 w-12 place-items-center rounded-xl bg-brand-900 text-gold-400">
          <CategoryIcon icon={category.icon} className="h-6 w-6" />
        </span>
        <div>
          <h1 className="text-2xl font-bold text-foreground">{isAr ? category.nameAr : category.nameEn}</h1>
          {category.parent && (
            <Link href={`/categories/${category.parent.slug}`} className="text-sm text-muted-foreground hover:underline">
              {isAr ? category.parent.nameAr : category.parent.nameEn}
            </Link>
          )}
        </div>
      </div>

      {isParent ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {category.children.map((c) => (
            <Link
              key={c.id}
              href={`/categories/${c.slug}`}
              className="rounded-xl border border-border bg-card p-5 font-semibold text-card-foreground transition hover:border-gold-500"
            >
              {isAr ? c.nameAr : c.nameEn}
            </Link>
          ))}
        </div>
      ) : (
        <>
          <div className="mb-6 flex flex-wrap gap-2">
            <Link
              href={`/categories/${slug}`}
              className={`rounded-full border px-3 py-1.5 text-sm ${!emirate ? "border-gold-500 bg-gold-500/10 text-brand-900 dark:text-gold-400" : "border-border text-muted-foreground"}`}
            >
              {isAr ? "الكل" : "All"}
            </Link>
            {emirates.map((e) => (
              <Link
                key={e.id}
                href={`/categories/${slug}?emirate=${e.slug}`}
                className={`rounded-full border px-3 py-1.5 text-sm ${emirate === e.slug ? "border-gold-500 bg-gold-500/10 text-brand-900 dark:text-gold-400" : "border-border text-muted-foreground"}`}
              >
                {isAr ? e.nameAr : e.nameEn}
              </Link>
            ))}
          </div>
          <CategoryListings slug={slug} emirate={emirate} page={page ? Number(page) : 1} />
        </>
      )}
    </div>
  );
}

async function CategoryListings({ slug, emirate, page }: { slug: string; emirate?: string; page: number }) {
  const t = await getTranslations("home");
  const [listings, total] = await getListingsByCategorySlug(slug, { emirateSlug: emirate, page });

  if (listings.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("featuredEmpty")}</p>;
  }

  return (
    <>
      <p className="mb-4 text-sm text-muted-foreground">{total} نتيجة</p>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {listings.map((l) => (
          <ListingCard key={l.id} listing={l} />
        ))}
      </div>
    </>
  );
}

export const dynamic = "force-dynamic";
