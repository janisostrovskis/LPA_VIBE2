"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import Button from "@/components/ui/Button";
import LanguageSwitcher from "./LanguageSwitcher";
import MobileNav from "./MobileNav";

interface HeaderProps {
  locale: string;
}

interface NavLink {
  key: string;
  href: string;
}

function buildNavLinks(locale: string): NavLink[] {
  return [
    { key: "home", href: `/${locale}` },
    { key: "about", href: `/${locale}/about` },
    { key: "join", href: `/${locale}/join` },
    { key: "trainings", href: `/${locale}/trainings` },
    { key: "directory", href: `/${locale}/directory` },
    { key: "news", href: `/${locale}/news` },
    { key: "resources", href: `/${locale}/resources` },
    { key: "verify", href: `/${locale}/verify` },
    { key: "contact", href: `/${locale}/contact` },
  ];
}

export default function Header({ locale }: HeaderProps): React.JSX.Element {
  const [scrolled, setScrolled] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const pathname = usePathname();
  const t = useTranslations("nav");
  const tUi = useTranslations("ui");

  useEffect(() => {
    function onScroll(): void {
      setScrolled(window.scrollY > 0);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navLinks = buildNavLinks(locale);

  function isActive(href: string): boolean {
    // Exact match for home, prefix match for others
    if (href === `/${locale}`) {
      return pathname === href;
    }
    return pathname.startsWith(href);
  }

  return (
    <>
      <header
        className={[
          "sticky top-0 h-20 z-[100]",
          "bg-lpa-surface/80 backdrop-blur-nav",
          "flex items-center justify-between px-10",
          "transition-shadow duration-300 ease-out",
          scrolled ? "shadow-cloud" : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        {/* Logo */}
        <Link
          href={`/${locale}`}
          className="font-display text-headline-md text-lpa-on-surface hover:text-lpa-secondary transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm"
          aria-label="LPA"
        >
          LPA
        </Link>

        {/* Desktop nav — center */}
        <nav
          className="hidden md:flex items-center gap-1"
          aria-label={t("home")}
        >
          {navLinks.map(({ key, href }) => (
            <Link
              key={key}
              href={href}
              className={[
                "font-label uppercase text-label-md font-medium tracking-[0.08em] px-3 py-1",
                "transition-colors duration-200 ease-out",
                "focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm",
                isActive(href)
                  ? "text-lpa-secondary border-b-2 border-lpa-secondary"
                  : "text-lpa-on-surface hover:text-lpa-secondary",
              ]
                .filter(Boolean)
                .join(" ")}
              aria-current={isActive(href) ? "page" : undefined}
            >
              {t(key as Parameters<typeof t>[0])}
            </Link>
          ))}
        </nav>

        {/* Right side: LanguageSwitcher + CTA + hamburger */}
        <div className="flex items-center gap-3">
          <div className="hidden md:block">
            <LanguageSwitcher currentLocale={locale} />
          </div>
          <div className="hidden md:block">
            <Button variant="primary" size="sm">
              {t("join")}
            </Button>
          </div>

          {/* Hamburger — mobile only */}
          <button
            type="button"
            className="md:hidden inline-flex items-center justify-center w-10 h-10 rounded-full text-lpa-on-surface hover:text-lpa-secondary hover:bg-lpa-surface-container transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary"
            aria-label={tUi("openMenu")}
            aria-expanded={mobileNavOpen}
            aria-controls="mobile-nav"
            onClick={() => setMobileNavOpen(true)}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              aria-hidden="true"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <line x1="2" y1="5" x2="18" y2="5" />
              <line x1="2" y1="10" x2="18" y2="10" />
              <line x1="2" y1="15" x2="18" y2="15" />
            </svg>
          </button>
        </div>
      </header>

      <MobileNav
        id="mobile-nav"
        open={mobileNavOpen}
        onClose={() => setMobileNavOpen(false)}
        locale={locale}
      />
    </>
  );
}
