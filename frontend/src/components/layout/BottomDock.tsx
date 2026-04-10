"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";

interface DockItem {
  key: string;
  href: string;
  icon: React.ReactNode;
}

interface BottomDockProps {
  locale: string;
}

// Inline SVG icons — 2px stroke, rounded caps, 24px viewBox
function IconHome(): React.JSX.Element {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 10.5L12 3l9 7.5V21a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V10.5Z" />
      <path d="M9 22V12h6v10" />
    </svg>
  );
}

function IconTrainings(): React.JSX.Element {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function IconDirectory(): React.JSX.Element {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="7" />
      <line x1="16.5" y1="16.5" x2="22" y2="22" />
    </svg>
  );
}

function IconNews(): React.JSX.Element {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z" />
      <line x1="7" y1="9" x2="17" y2="9" />
      <line x1="7" y1="13" x2="17" y2="13" />
      <line x1="7" y1="17" x2="12" y2="17" />
    </svg>
  );
}

function IconProfile(): React.JSX.Element {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
    </svg>
  );
}

function buildDockItems(locale: string): DockItem[] {
  return [
    { key: "home", href: `/${locale}`, icon: <IconHome /> },
    { key: "trainings", href: `/${locale}/trainings`, icon: <IconTrainings /> },
    { key: "directory", href: `/${locale}/directory`, icon: <IconDirectory /> },
    { key: "news", href: `/${locale}/news`, icon: <IconNews /> },
    { key: "profile", href: `/${locale}/profile`, icon: <IconProfile /> },
  ];
}

export default function BottomDock({ locale }: BottomDockProps): React.JSX.Element {
  const pathname = usePathname();
  const t = useTranslations("nav");
  const dockItems = buildDockItems(locale);

  function isActive(href: string): boolean {
    if (href === `/${locale}`) {
      return pathname === href;
    }
    return pathname.startsWith(href);
  }

  return (
    <nav
      className="fixed bottom-6 left-1/2 -translate-x-1/2 md:hidden z-[100]"
      aria-label="Mobile navigation"
    >
      <div className="bg-lpa-surface/80 backdrop-blur-nav rounded-pill shadow-cloud px-4 py-3 flex gap-2">
        {dockItems.map(({ key, href, icon }) => {
          const active = isActive(href);
          const navKey = key === "profile" ? "home" : (key as Parameters<typeof t>[0]);
          // Profile key not in nav translations; use key directly as label
          const label = key === "profile" ? "Profile" : t(navKey);
          return (
            <Link
              key={key}
              href={href}
              aria-current={active ? "page" : undefined}
              aria-label={label}
              className={[
                "min-h-12 min-w-12 flex flex-col items-center justify-center gap-0.5",
                "font-label text-label-sm uppercase tracking-[0.08em]",
                "transition-colors duration-200 ease-out",
                "rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2",
                active ? "text-lpa-secondary" : "text-lpa-on-surface-variant hover:text-lpa-secondary",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              {icon}
              <span className="sr-only md:not-sr-only">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
