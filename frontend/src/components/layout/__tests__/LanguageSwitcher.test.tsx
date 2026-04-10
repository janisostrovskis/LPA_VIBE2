import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LanguageSwitcher from "../LanguageSwitcher";

const mockPush = vi.fn();

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/lv/about",
  useRouter: () => ({ push: mockPush }),
}));

describe("LanguageSwitcher", () => {
  beforeEach(() => {
    mockPush.mockReset();
  });

  it("renders 3 locale buttons", () => {
    render(<LanguageSwitcher currentLocale="lv" />);
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(3);
  });

  it("renders LV, EN, RU buttons", () => {
    render(<LanguageSwitcher currentLocale="lv" />);
    expect(screen.getByRole("button", { name: "LV" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "EN" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "RU" })).toBeTruthy();
  });

  it("active locale button has aria-pressed=true", () => {
    render(<LanguageSwitcher currentLocale="lv" />);
    const lvBtn = screen.getByRole("button", { name: "LV" });
    expect(lvBtn.getAttribute("aria-pressed")).toBe("true");
  });

  it("inactive locale buttons have aria-pressed=false", () => {
    render(<LanguageSwitcher currentLocale="lv" />);
    const enBtn = screen.getByRole("button", { name: "EN" });
    expect(enBtn.getAttribute("aria-pressed")).toBe("false");
    const ruBtn = screen.getByRole("button", { name: "RU" });
    expect(ruBtn.getAttribute("aria-pressed")).toBe("false");
  });

  it("active locale has font-bold and text-lpa-secondary classes", () => {
    render(<LanguageSwitcher currentLocale="en" />);
    const enBtn = screen.getByRole("button", { name: "EN" });
    expect(enBtn.className).toContain("font-bold");
    expect(enBtn.className).toContain("text-lpa-secondary");
  });

  it("clicking inactive locale calls router.push with new locale path", async () => {
    const user = userEvent.setup();
    render(<LanguageSwitcher currentLocale="lv" />);
    await user.click(screen.getByRole("button", { name: "EN" }));
    expect(mockPush).toHaveBeenCalledWith("/en/about");
  });

  it("clicking active locale still calls router.push", async () => {
    const user = userEvent.setup();
    render(<LanguageSwitcher currentLocale="lv" />);
    await user.click(screen.getByRole("button", { name: "LV" }));
    expect(mockPush).toHaveBeenCalledWith("/lv/about");
  });
});
