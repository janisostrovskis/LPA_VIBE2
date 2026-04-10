import { getTranslations } from "next-intl/server";
import { setRequestLocale } from "next-intl/server";
import { type Locale } from "@/lib/i18n";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale as Locale);
  const t = await getTranslations({ locale: locale as Locale, namespace: "site" });

  return (
    <div className="min-h-screen bg-lpa-surface text-lpa-on-surface flex flex-col items-center justify-center p-lpa-xxl">
      <h1 className="font-display text-display-lg text-lpa-on-surface tracking-tight text-center">
        {t("name")}
      </h1>
      <p className="mt-lpa-s font-body text-body-lg text-lpa-on-surface-variant text-center">
        {t("tagline")}
      </p>
    </div>
  );
}
