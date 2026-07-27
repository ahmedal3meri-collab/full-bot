import Image from "next/image";
import { getLocale, getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { BadgeCheck } from "lucide-react";

type CompanyCardData = {
  slug: string;
  name: string;
  logoUrl: string | null;
  descriptionAr: string | null;
  descriptionEn: string | null;
  isVerified: boolean;
};

export async function CompanyCard({ company }: { company: CompanyCardData }) {
  const locale = await getLocale();
  const t = await getTranslations("home");
  const isAr = locale === "ar";
  const desc = (isAr ? company.descriptionAr : company.descriptionEn) || company.descriptionAr;

  return (
    <Link
      href={`/companies/${company.slug}`}
      className="flex items-center gap-4 rounded-xl border border-border bg-card p-4 transition hover:border-gold-500"
    >
      <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-full bg-muted">
        {company.logoUrl ? (
          <Image src={company.logoUrl} alt={company.name} fill className="object-cover" />
        ) : (
          <span className="grid h-full w-full place-items-center text-lg font-bold text-brand-700">
            {company.name.charAt(0)}
          </span>
        )}
      </div>
      <div className="min-w-0">
        <p className="flex items-center gap-1.5 truncate font-semibold text-card-foreground">
          {company.name}
          {company.isVerified && <BadgeCheck className="h-4 w-4 shrink-0 text-gold-500" aria-label={t("verified")} />}
        </p>
        <p className="line-clamp-1 text-xs text-muted-foreground">{desc}</p>
      </div>
    </Link>
  );
}
