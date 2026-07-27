import Image from "next/image";
import { getLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { formatAed } from "@/lib/format";
import { BadgeCheck, MapPin } from "lucide-react";

type ListingCardData = {
  id: string;
  titleAr: string;
  titleEn: string | null;
  price: unknown; // Prisma Decimal (serialized to string across the RSC boundary)
  isPriceNegotiable: boolean;
  verificationStatus: string;
  images: { url: string }[];
  category: { nameAr: string; nameEn: string };
  emirate: { nameAr: string; nameEn: string };
};

export async function ListingCard({ listing }: { listing: ListingCardData }) {
  const locale = await getLocale();
  const isAr = locale === "ar";
  const title = (isAr ? listing.titleAr : listing.titleEn) || listing.titleAr;
  const image = listing.images[0]?.url ?? "/demo/placeholder.svg";

  return (
    <Link
      href={`/listings/${listing.id}`}
      className="group overflow-hidden rounded-xl border border-border bg-card transition hover:shadow-lg hover:shadow-brand-900/5"
    >
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-muted">
        <Image
          src={image}
          alt={title}
          fill
          className="object-cover transition duration-300 group-hover:scale-105"
          sizes="(max-width: 768px) 100vw, 25vw"
        />
        {listing.verificationStatus === "VERIFIED" && (
          <span className="absolute top-2 start-2 inline-flex items-center gap-1 rounded-full bg-brand-900/90 px-2 py-1 text-xs font-medium text-gold-400">
            <BadgeCheck className="h-3.5 w-3.5" />
            {isAr ? "موثّق" : "Verified"}
          </span>
        )}
      </div>
      <div className="space-y-1.5 p-3">
        <p className="line-clamp-1 text-sm font-semibold text-card-foreground">{title}</p>
        <p className="text-base font-bold text-brand-700 dark:text-gold-400">
          {formatAed(String(listing.price), locale)}
          {listing.isPriceNegotiable && <span className="ms-1 text-xs font-normal text-muted-foreground">{isAr ? "(قابل للتفاوض)" : "(negotiable)"}</span>}
        </p>
        <p className="flex items-center gap-1 text-xs text-muted-foreground">
          <MapPin className="h-3.5 w-3.5" />
          {isAr ? listing.emirate.nameAr : listing.emirate.nameEn}
        </p>
      </div>
    </Link>
  );
}
