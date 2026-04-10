"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { locales, type Locale } from "@/lib/i18n";

interface LanguageSwitcherProps {
  currentLocale: string;
}

export default function LanguageSwitcher({
  currentLocale,
}: LanguageSwitcherProps): React.JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const t = useTranslations("languages");

  function handleLocaleChange(newLocale: Locale): void {
    // Replace the locale segment: /lv/foo -> /en/foo
    const segments = pathname.split("/");
    // segments[0] = "" (leading slash), segments[1] = locale
    segments[1] = newLocale;
    router.push(segments.join("/"));
  }

  return (
    <div
      className="flex items-center gap-1"
      role="group"
      aria-label={t("lv")}
    >
      {locales.map((locale) => {
        const isActive = locale === currentLocale;
        return (
          <button
            key={locale}
            type="button"
            onClick={() => handleLocaleChange(locale)}
            aria-pressed={isActive}
            lang={locale}
            className={[
              "inline-flex items-center justify-center rounded-pill px-2 py-1",
              "font-label text-label-sm uppercase tracking-[0.08em]",
              "transition-colors duration-200 ease-out",
              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2",
              isActive
                ? "font-bold text-lpa-secondary"
                : "text-lpa-on-surface-variant hover:text-lpa-secondary",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            {locale.toUpperCase()}
          </button>
        );
      })}
    </div>
  );
}
