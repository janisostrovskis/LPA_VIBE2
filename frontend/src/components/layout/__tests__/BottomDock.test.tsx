import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import BottomDock from "../BottomDock";

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
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
    "aria-label"?: string;
    "aria-current"?: string;
  }) => (
    <a href={href} className={className} aria-label={ariaLabel} aria-current={ariaCurrent}>
      {children}
    </a>
  ),
}));

describe("BottomDock", () => {
  it("renders 5 nav items", () => {
    render(<BottomDock locale="lv" />);
    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(5);
  });

  it("each item has min-h-12 and min-w-12 tap target classes", () => {
    render(<BottomDock locale="lv" />);
    const links = screen.getAllByRole("link");
    links.forEach((link) => {
      expect(link.className).toContain("min-h-12");
      expect(link.className).toContain("min-w-12");
    });
  });

  it("nav element has md:hidden class", () => {
    render(<BottomDock locale="lv" />);
    const nav = screen.getByRole("navigation", { name: "Mobile navigation" });
    expect(nav.className).toContain("md:hidden");
  });

  it("active item (home at /lv) has aria-current=page", () => {
    render(<BottomDock locale="lv" />);
    const homeLink = screen.getByRole("link", { name: "home" });
    expect(homeLink.getAttribute("aria-current")).toBe("page");
  });

  it("inactive items do not have aria-current", () => {
    render(<BottomDock locale="lv" />);
    const trainingsLink = screen.getByRole("link", { name: "trainings" });
    expect(trainingsLink.getAttribute("aria-current")).toBeNull();
  });

  it("renders nav links with correct locale hrefs", () => {
    render(<BottomDock locale="en" />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/en");
    expect(hrefs).toContain("/en/trainings");
    expect(hrefs).toContain("/en/profile");
  });
});
