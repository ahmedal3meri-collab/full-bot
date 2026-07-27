import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { LoginForm } from "@/components/auth/login-form";

export default async function LoginPage() {
  const t = await getTranslations("auth");

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 px-4 py-16 sm:px-6">
      <h1 className="text-center text-2xl font-bold text-foreground">{t("loginTitle")}</h1>
      <div className="rounded-2xl border border-border bg-card p-6">
        <LoginForm />
      </div>
      <p className="text-center text-sm text-muted-foreground">
        {t("noAccount")}{" "}
        <Link href="/register" className="font-medium text-brand-700 hover:underline dark:text-gold-400">
          {t("registerTitle")}
        </Link>
      </p>
    </div>
  );
}
