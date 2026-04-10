import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MobileNav from "../MobileNav";

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
    onClick,
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
    onClick?: () => void;
  }) => (
    <a href={href} className={className} onClick={onClick}>
      {children}
    </a>
  ),
}));

vi.mock("../LanguageSwitcher", () => ({
  default: ({ currentLocale }: { currentLocale: string }) => (
    <div data-testid="language-switcher" data-locale={currentLocale} />
  ),
}));

// createPortal renders into document.body in tests — mock it to render inline
vi.mock("react-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-dom")>();
  return {
    ...actual,
    createPortal: (node: React.ReactNode) => node,
  };
});

describe("MobileNav", () => {
  const onClose = vi.fn();

  beforeEach(() => {
    onClose.mockReset();
  });

  it("renders nothing when open=false", () => {
    const { container } = render(
      <MobileNav open={false} onClose={onClose} locale="lv" />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders nav links when open=true", () => {
    render(<MobileNav open={true} onClose={onClose} locale="lv" />);
    expect(screen.getByRole("dialog")).toBeTruthy();
  });

  it("renders all 9 nav links when open", () => {
    render(<MobileNav open={true} onClose={onClose} locale="lv" />);
    const links = screen.getAllByRole("link");
    // 9 nav links (not counting LanguageSwitcher which is mocked)
    expect(links.length).toBeGreaterThanOrEqual(9);
  });

  it("has overlay with backdrop-blur-modal class", () => {
    render(<MobileNav open={true} onClose={onClose} locale="lv" />);
    const overlay = document.querySelector(".backdrop-blur-modal");
    expect(overlay).toBeTruthy();
  });

  it("close button calls onClose", async () => {
    const user = userEvent.setup();
    render(<MobileNav open={true} onClose={onClose} locale="lv" />);
    const closeBtn = screen.getByRole("button", { name: "closeMenu" });
    await user.click(closeBtn);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("clicking overlay calls onClose", async () => {
    const user = userEvent.setup();
    render(<MobileNav open={true} onClose={onClose} locale="lv" />);
    const overlay = document.querySelector(".fixed.inset-0") as HTMLElement;
    // Click the overlay div directly
    await user.click(overlay);
    expect(onClose).toHaveBeenCalled();
  });

  it("nav links include locale-prefixed hrefs", () => {
    render(<MobileNav open={true} onClose={onClose} locale="lv" />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/lv");
    expect(hrefs).toContain("/lv/about");
    expect(hrefs).toContain("/lv/trainings");
  });
});
