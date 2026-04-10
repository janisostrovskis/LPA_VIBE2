import Link from "next/link";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { type Locale } from "@/lib/i18n";
import Button from "@/components/ui/Button";

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale as Locale);
  const t = await getTranslations({ locale: locale as Locale, namespace: "pages.home" });

  return (
    <main className="min-h-screen bg-lpa-surface text-lpa-on-surface flex flex-col items-center justify-center p-lpa-xxl">
      <h1 className="font-display text-display-lg text-lpa-on-surface tracking-tight text-center mb-lpa-s">
        {t("title")}
      </h1>
      <p className="font-body text-body-lg text-lpa-on-surface-variant text-center mb-lpa-l">
        {t("subtitle")}
      </p>
      <Link href={`/${locale}/join`}>
        <Button variant="primary">{t("cta")}</Button>
      </Link>
    </main>
  );
}
