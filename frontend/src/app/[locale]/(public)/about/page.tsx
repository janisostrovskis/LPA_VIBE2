import { getTranslations, setRequestLocale } from "next-intl/server";
import { type Locale } from "@/lib/i18n";

export default async function AboutPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale as Locale);
  const t = await getTranslations({ locale: locale as Locale, namespace: "pages.about" });

  return (
    <main className="max-w-5xl mx-auto px-lpa-m py-lpa-xl">
      <h1 className="font-display text-display-lg text-lpa-on-surface mb-lpa-s">{t("title")}</h1>
      <p className="font-body text-body-lg text-lpa-on-surface-variant">{t("subtitle")}</p>
    </main>
  );
}
