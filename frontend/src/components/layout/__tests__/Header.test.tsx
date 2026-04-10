import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Header from "../Header";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/lv",
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    className,
    "aria-label": ariaLabel,
    "aria-current": ariaCurrent,
    onClick,
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
    "aria-label"?: string;
    "aria-current"?: string;
    onClick?: () => void;
  }) => (
    <a href={href} className={className} aria-label={ariaLabel} aria-current={ariaCurrent} onClick={onClick}>
      {children}
    </a>
  ),
}));

vi.mock("../MobileNav", () => ({
  default: ({ open, onClose, locale }: { open: boolean; onClose: () => void; locale: string }) =>
    open ? <div data-testid="mobile-nav" data-locale={locale}><button onClick={onClose}>close</button></div> : null,
}));

vi.mock("../LanguageSwitcher", () => ({
  default: ({ currentLocale }: { currentLocale: string }) => (
    <div data-testid="language-switcher" data-locale={currentLocale} />
  ),
}));

describe("Header", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the LPA logo link", () => {
    render(<Header locale="lv" />);
    const logo = screen.getByRole("link", { name: "LPA" });
    expect(logo).toBeTruthy();
  });

  it("desktop nav element exists in document", () => {
    render(<Header locale="lv" />);
    const navEl = document.querySelector("nav.hidden.md\\:flex");
    expect(navEl).not.toBeNull();
  });

  it("desktop nav has hidden md:flex classes", () => {
    render(<Header locale="lv" />);
    const navEl = document.querySelector("nav.hidden.md\\:flex");
    expect(navEl?.className).toContain("hidden");
    expect(navEl?.className).toContain("md:flex");
  });

  it("renders hamburger button for mobile", () => {
    render(<Header locale="lv" />);
    const hamburger = screen.getByRole("button", { name: "openMenu" });
    expect(hamburger).toBeTruthy();
  });

  it("hamburger button toggles MobileNav open", async () => {
    const user = userEvent.setup();
    render(<Header locale="lv" />);
    expect(screen.queryByTestId("mobile-nav")).toBeNull();
    await user.click(screen.getByRole("button", { name: "openMenu" }));
    expect(screen.getByTestId("mobile-nav")).toBeTruthy();
  });

  it("renders LanguageSwitcher", () => {
    render(<Header locale="lv" />);
    const switcher = screen.getByTestId("language-switcher");
    expect(switcher).toBeTruthy();
  });

  it("nav links include all expected routes for lv locale", () => {
    render(<Header locale="lv" />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/lv");
    expect(hrefs).toContain("/lv/about");
    expect(hrefs).toContain("/lv/trainings");
  });
});
