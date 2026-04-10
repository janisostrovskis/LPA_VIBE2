"use client";

import React, { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { buildNavLinks } from "@/lib/navigation";
import { getFocusableElements } from "@/lib/focus-trap";
import LanguageSwitcher from "./LanguageSwitcher";

interface MobileNavProps {
  id?: string;
  open: boolean;
  onClose: () => void;
  locale: string;
}

export default function MobileNav({
  id,
  open,
  onClose,
  locale,
}: MobileNavProps): React.JSX.Element | null {
  const drawerRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const t = useTranslations("nav");
  const tUi = useTranslations("ui");
  const navLinks = buildNavLinks(locale);

  useEffect(() => {
    if (!open) return;

    previousFocusRef.current = document.activeElement as HTMLElement;

    const frame = requestAnimationFrame(() => {
      if (!drawerRef.current) return;
      const focusable = getFocusableElements(drawerRef.current);
      const first = focusable[0];
      if (first) {
        first.focus();
      } else {
        drawerRef.current.focus();
      }
    });

    function handleKeyDown(e: KeyboardEvent): void {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key === "Tab" && drawerRef.current) {
        const focusable = getFocusableElements(drawerRef.current);
        if (focusable.length === 0) return;
        const first = focusable[0] as HTMLElement | undefined;
        const last = focusable[focusable.length - 1] as HTMLElement | undefined;
        if (!first || !last) return;
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      cancelAnimationFrame(frame);
      document.removeEventListener("keydown", handleKeyDown);
      previousFocusRef.current?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  const drawer = (
    <div
      className="fixed inset-0 z-[150] bg-lpa-surface/80 backdrop-blur-modal"
      onClick={onClose}
    >
      <div
        id={id}
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-label={tUi("openMenu")}
        tabIndex={-1}
        className="relative h-full flex flex-col focus-visible:outline-none"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <div className="flex justify-end px-6 pt-6">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center justify-center w-10 h-10 rounded-full text-lpa-on-surface hover:text-lpa-secondary hover:bg-lpa-surface-container transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary"
            aria-label={tUi("closeMenu")}
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
              <line x1="4" y1="4" x2="16" y2="16" />
              <line x1="16" y1="4" x2="4" y2="16" />
            </svg>
          </button>
        </div>

        {/* Nav links */}
        <nav
          className="flex flex-col px-10 pt-8 gap-8"
          aria-label={tUi("openMenu")}
        >
          {navLinks.map(({ key, href }) => (
            <Link
              key={key}
              href={href}
              onClick={onClose}
              className={[
                "font-display text-headline-md text-lpa-on-surface",
                "min-h-12 flex items-center",
                "hover:text-lpa-secondary transition-colors duration-200 ease-out",
                "focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              {t(key as Parameters<typeof t>[0])}
            </Link>
          ))}
        </nav>

        {/* Language switcher at bottom */}
        <div className="mt-auto px-10 pb-lpa-xxxl">
          <LanguageSwitcher currentLocale={locale} />
        </div>
      </div>
    </div>
  );

  return createPortal(drawer, document.body);
}
