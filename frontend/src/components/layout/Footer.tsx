import React from "react";
import Link from "next/link";
import { getTranslations } from "next-intl/server";

interface FooterProps {
  locale: string;
}

export default async function Footer({ locale }: FooterProps): Promise<React.JSX.Element> {
  const tSite = await getTranslations({ locale, namespace: "site" });
  const tFooter = await getTranslations({ locale, namespace: "footer" });

  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-lpa-surface-container-low py-lpa-xl px-lpa-l">
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-lpa-l mb-lpa-l">
          {/* Column 1: Brand */}
          <div className="flex flex-col gap-lpa-xs">
            <span className="font-display text-headline-md text-lpa-on-surface">
              LPA
            </span>
            <p className="font-body text-body-md text-lpa-on-surface-variant">
              {tSite("name")}
            </p>
            <p className="font-body text-body-md text-lpa-on-surface-variant">
              {tSite("tagline")}
            </p>
          </div>

          {/* Column 2: Legal links */}
          <div className="flex flex-col gap-lpa-xs">
            <nav aria-label="Legal">
              <ul className="flex flex-col gap-2 list-none p-0 m-0">
                <li>
                  <Link
                    href={`/${locale}/privacy`}
                    className="font-body text-body-md text-lpa-on-surface-variant hover:text-lpa-secondary transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm"
                  >
                    {tFooter("privacy")}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${locale}/terms`}
                    className="font-body text-body-md text-lpa-on-surface-variant hover:text-lpa-secondary transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm"
                  >
                    {tFooter("terms")}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${locale}/cookies`}
                    className="font-body text-body-md text-lpa-on-surface-variant hover:text-lpa-secondary transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm"
                  >
                    {tFooter("cookies")}
                  </Link>
                </li>
              </ul>
            </nav>
          </div>

          {/* Column 3: Contact placeholder */}
          <div className="flex flex-col gap-lpa-xs">
            <p className="font-body text-body-md text-lpa-on-surface-variant">
              info@pilates.lv
            </p>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="border-t border-lpa-outline-variant pt-lpa-s">
          <p className="font-label text-label-sm text-lpa-on-surface-variant">
            &copy; {currentYear} {tSite("name")}
          </p>
        </div>
      </div>
    </footer>
  );
}
