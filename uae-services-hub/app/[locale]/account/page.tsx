import { redirect } from "next/navigation";
import { getLocale, getTranslations } from "next-intl/server";
import { getCurrentUser } from "@/lib/auth/session";
import { prisma } from "@/lib/db/client";

export default async function AccountPage() {
  const user = await getCurrentUser();
  const locale = await getLocale();
  if (!user) redirect(`/${locale}/login`);

  const [listingsCount, favoritesCount, requestsCount] = await Promise.all([
    prisma.listing.count({ where: { ownerId: user.id } }),
    prisma.favorite.count({ where: { userId: user.id } }),
    prisma.serviceRequest.count({ where: { userId: user.id } }),
  ]);

  const t = await getTranslations("auth");

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <div className="rounded-2xl border border-border bg-card p-6">
        <h1 className="text-xl font-bold text-card-foreground">{user.fullName}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{user.email ?? user.phone}</p>
        <p className="mt-1 text-sm text-muted-foreground">{t("emirate")}: {user.emirateId ?? "—"}</p>
        <p className="mt-1 text-xs text-gold-600">{user.role?.nameAr ?? user.roleId}</p>

        <div className="mt-6 grid grid-cols-3 gap-4 text-center">
          <Stat label="إعلاناتي" value={listingsCount} />
          <Stat label="المفضلة" value={favoritesCount} />
          <Stat label="طلباتي" value={requestsCount} />
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl bg-muted p-4">
      <p className="text-2xl font-bold text-brand-700 dark:text-gold-400">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
