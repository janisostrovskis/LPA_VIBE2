import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Badge from "../Badge";

describe("Badge", () => {
  it("renders children", () => {
    render(<Badge>Member</Badge>);
    expect(screen.getByText("Member")).toBeTruthy();
  });

  it("primary variant applies primary-container color classes", () => {
    render(<Badge variant="primary">Primary</Badge>);
    const badge = screen.getByText("Primary");
    expect(badge.className).toContain("bg-lpa-primary-container");
    expect(badge.className).toContain("text-lpa-on-primary-container");
  });

  it("secondary variant applies secondary-container color classes", () => {
    render(<Badge variant="secondary">Secondary</Badge>);
    const badge = screen.getByText("Secondary");
    expect(badge.className).toContain("bg-lpa-secondary-container");
    expect(badge.className).toContain("text-lpa-on-secondary-container");
  });

  it("tertiary variant applies tertiary-container color classes", () => {
    render(<Badge variant="tertiary">Tertiary</Badge>);
    const badge = screen.getByText("Tertiary");
    expect(badge.className).toContain("bg-lpa-tertiary-container");
    expect(badge.className).toContain("text-lpa-on-tertiary-container");
  });

  it("outline variant applies transparent bg and border classes", () => {
    render(<Badge variant="outline">Outline</Badge>);
    const badge = screen.getByText("Outline");
    expect(badge.className).toContain("bg-transparent");
    expect(badge.className).toContain("border-lpa-outline");
    expect(badge.className).toContain("text-lpa-on-surface");
  });

  it("all variants have pill shape and uppercase classes", () => {
    const variants = ["primary", "secondary", "tertiary", "outline"] as const;
    variants.forEach((variant) => {
      const { unmount } = render(<Badge variant={variant}>{variant}</Badge>);
      const badge = screen.getByText(variant);
      expect(badge.className).toContain("rounded-pill");
      expect(badge.className).toContain("uppercase");
      unmount();
    });
  });
});
