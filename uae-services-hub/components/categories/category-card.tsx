import { getLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { CategoryIcon } from "@/lib/modules/categories/icons";

type CategoryCardData = {
  slug: string;
  nameAr: string;
  nameEn: string;
  icon: string | null;
  children: { slug: string; nameAr: string; nameEn: string }[];
};

export async function CategoryCard({ category }: { category: CategoryCardData }) {
  const locale = await getLocale();
  const isAr = locale === "ar";

  return (
    <Link
      href={`/categories/${category.slug}`}
      className="group flex flex-col gap-3 rounded-xl border border-border bg-card p-5 transition hover:-translate-y-0.5 hover:border-gold-500 hover:shadow-lg hover:shadow-brand-900/5"
    >
      <span className="grid h-11 w-11 place-items-center rounded-lg bg-brand-900 text-gold-400 transition group-hover:bg-gold-500 group-hover:text-brand-950">
        <CategoryIcon icon={category.icon} className="h-5 w-5" />
      </span>
      <div>
        <p className="font-semibold text-card-foreground">{isAr ? category.nameAr : category.nameEn}</p>
        <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">
          {category.children.slice(0, 3).map((c) => (isAr ? c.nameAr : c.nameEn)).join(" · ")}
        </p>
      </div>
    </Link>
  );
}
