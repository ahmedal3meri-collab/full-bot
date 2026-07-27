import Image from "next/image";
import { notFound } from "next/navigation";
import { getLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { getListingById } from "@/lib/modules/listings/queries";
import { formatAed } from "@/lib/format";
import { MapPin, Phone, MessageCircle, BadgeCheck } from "lucide-react";

export default async function ListingDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const locale = await getLocale();
  const isAr = locale === "ar";

  const listing = await getListingById(id);
  if (!listing || listing.status !== "PUBLISHED") notFound();

  const title = (isAr ? listing.titleAr : listing.titleEn) || listing.titleAr;
  const description = (isAr ? listing.descriptionAr : listing.descriptionEn) || listing.descriptionAr;
  const coverImage = listing.images[0]?.url ?? "/demo/placeholder.svg";

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <nav className="mb-4 text-sm text-muted-foreground">
        <Link href={`/categories/${listing.category.slug}`} className="hover:underline">
          {isAr ? listing.category.nameAr : listing.category.nameEn}
        </Link>
      </nav>

      <div className="grid gap-8 md:grid-cols-3">
        <div className="md:col-span-2">
          <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl bg-muted">
            <Image src={coverImage} alt={title} fill className="object-cover" priority />
            {listing.verificationStatus === "VERIFIED" && (
              <span className="absolute top-3 start-3 inline-flex items-center gap-1 rounded-full bg-brand-900/90 px-3 py-1.5 text-sm font-medium text-gold-400">
                <BadgeCheck className="h-4 w-4" /> {isAr ? "موثّق" : "Verified"}
              </span>
            )}
          </div>

          {listing.images.length > 1 && (
            <div className="mt-3 grid grid-cols-5 gap-2">
              {listing.images.slice(1, 6).map((img) => (
                <div key={img.id} className="relative aspect-square overflow-hidden rounded-lg bg-muted">
                  <Image src={img.url} alt="" fill className="object-cover" />
                </div>
              ))}
            </div>
          )}

          <h1 className="mt-6 text-2xl font-bold text-foreground">{title}</h1>
          <p className="mt-2 flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            {isAr ? listing.emirate.nameAr : listing.emirate.nameEn}
            {listing.city && ` · ${isAr ? listing.city.nameAr : listing.city.nameEn}`}
          </p>

          <p className="mt-6 whitespace-pre-line text-sm leading-relaxed text-foreground/90">{description}</p>

          {listing.attributes.length > 0 && (
            <div className="mt-8">
              <h2 className="mb-3 font-semibold text-foreground">{isAr ? "التفاصيل" : "Details"}</h2>
              <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {listing.attributes.map((a) => (
                  <div key={a.id} className="rounded-lg bg-muted p-3">
                    <dt className="text-xs text-muted-foreground">
                      {isAr ? a.attributeDefinition.labelAr : a.attributeDefinition.labelEn}
                    </dt>
                    <dd className="mt-0.5 text-sm font-medium text-foreground">
                      {a.valueString ?? a.valueNumber?.toString() ?? (a.valueBoolean != null ? (a.valueBoolean ? "✓" : "—") : "—")}
                      {a.attributeDefinition.unit ? ` ${a.attributeDefinition.unit}` : ""}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-border bg-card p-5">
            <p className="text-2xl font-bold text-brand-700 dark:text-gold-400">
              {formatAed(String(listing.price), locale)}
            </p>
            {listing.isPriceNegotiable && (
              <p className="mt-1 text-xs text-muted-foreground">{isAr ? "السعر قابل للتفاوض" : "Negotiable"}</p>
            )}

            <div className="mt-5 flex flex-col gap-2">
              <a
                href={`tel:${listing.contactPhone}`}
                className="btn-primary flex items-center justify-center gap-2"
              >
                <Phone className="h-4 w-4" /> {isAr ? "اتصال" : "Call"}
              </a>
              {listing.whatsapp && (
                <a
                  href={`https://wa.me/${listing.whatsapp.replace(/[^0-9]/g, "")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 rounded-lg border border-success/40 px-4 py-2.5 text-sm font-semibold text-success transition hover:bg-success/10"
                >
                  <MessageCircle className="h-4 w-4" /> WhatsApp
                </a>
              )}
            </div>
          </div>

          {listing.company && (
            <Link
              href={`/companies/${listing.company.slug}`}
              className="flex items-center gap-3 rounded-2xl border border-border bg-card p-4 transition hover:border-gold-500"
            >
              <span className="grid h-11 w-11 place-items-center rounded-full bg-muted text-sm font-bold text-brand-700">
                {listing.company.name.charAt(0)}
              </span>
              <div className="min-w-0">
                <p className="flex items-center gap-1 truncate text-sm font-semibold text-card-foreground">
                  {listing.company.name}
                  {listing.company.isVerified && <BadgeCheck className="h-4 w-4 shrink-0 text-gold-500" />}
                </p>
                <p className="text-xs text-muted-foreground">{isAr ? "عرض صفحة الشركة" : "View company page"}</p>
              </div>
            </Link>
          )}
        </aside>
      </div>
    </div>
  );
}

export const dynamic = "force-dynamic";
