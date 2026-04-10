export interface NavLink {
  key: string;
  href: string;
}

export function buildNavLinks(locale: string): NavLink[] {
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

export function isActiveRoute(
  href: string,
  pathname: string,
  locale: string,
): boolean {
  if (href === `/${locale}`) {
    return pathname === href;
  }
  return pathname.startsWith(href);
}
