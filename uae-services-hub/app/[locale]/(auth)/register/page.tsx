import { getLocale, getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { prisma } from "@/lib/db/client";
import { RegisterForm } from "@/components/auth/register-form";

export default async function RegisterPage() {
  const t = await getTranslations("auth");
  const locale = await getLocale();
  const emirates = await prisma.emirate.findMany({ orderBy: { sortOrder: "asc" } });

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-4 py-16 sm:px-6">
      <h1 className="text-center text-2xl font-bold text-foreground">{t("registerTitle")}</h1>
      <div className="rounded-2xl border border-border bg-card p-6">
        <RegisterForm emirates={emirates} locale={locale} />
      </div>
      <p className="text-center text-sm text-muted-foreground">
        {t("haveAccount")}{" "}
        <Link href="/login" className="font-medium text-brand-700 hover:underline dark:text-gold-400">
          {t("loginTitle")}
        </Link>
      </p>
    </div>
  );
}
