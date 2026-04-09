export const locales = ["lv", "en", "ru"] as const;
export const defaultLocale = "lv" as const;

export type Locale = (typeof locales)[number];
