import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Card from "../Card";

describe("Card", () => {
  it("renders children", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeTruthy();
  });

  it("base variant has surface-container-lowest class", () => {
    const { container } = render(<Card variant="base">Base</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain("bg-lpa-surface-container-lowest");
  });

  it("feature variant has surface-container class (not lowest)", () => {
    const { container } = render(<Card variant="feature">Feature</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain("bg-lpa-surface-container");
    expect(card.className).not.toContain("bg-lpa-surface-container-lowest");
  });

  it("hover prop adds translate and shadow transition classes", () => {
    const { container } = render(<Card hover>Hoverable</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain("hover:-translate-y-0.5");
    expect(card.className).toContain("hover:shadow-cloud");
    expect(card.className).toContain("transition-all");
  });

  it("without hover prop, no translate or shadow classes", () => {
    const { container } = render(<Card>Static</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).not.toContain("hover:-translate-y-0.5");
    expect(card.className).not.toContain("hover:shadow-cloud");
  });
});
