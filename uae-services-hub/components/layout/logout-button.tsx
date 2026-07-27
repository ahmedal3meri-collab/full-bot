"use client";

import { useTransition } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { logoutAction } from "@/lib/modules/auth/actions";

export function LogoutButton() {
  const t = useTranslations("common");
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={isPending}
      onClick={() =>
        startTransition(async () => {
          await logoutAction();
          router.push("/");
          router.refresh();
        })
      }
      className="rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground/80 transition hover:bg-muted disabled:opacity-60"
    >
      {t("logout")}
    </button>
  );
}
