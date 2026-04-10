import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Button from "../Button";

describe("Button", () => {
  it("renders children text", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: "Click me" })).toBeTruthy();
  });

  it("primary variant has gradient classes", () => {
    render(<Button variant="primary">Primary</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("from-lpa-primary");
    expect(btn.className).toContain("to-lpa-primary-container");
  });

  it("secondary variant has secondary-container classes", () => {
    render(<Button variant="secondary">Secondary</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-lpa-secondary-container");
    expect(btn.className).toContain("text-lpa-on-secondary-container");
  });

  it("text variant has transparent background", () => {
    render(<Button variant="text">Text</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-transparent");
  });

  it("disabled state has disabled attribute and opacity class", () => {
    render(<Button disabled>Disabled</Button>);
    const btn = screen.getByRole("button");
    expect(btn).toHaveProperty("disabled", true);
    expect(btn.className).toContain("disabled:opacity-50");
  });

  it("loading state has aria-busy and spinner element", () => {
    render(<Button loading>Loading</Button>);
    const btn = screen.getByRole("button");
    expect(btn.getAttribute("aria-busy")).toBe("true");
    const spinner = btn.querySelector(".animate-spin");
    expect(spinner).not.toBeNull();
  });

  it("onClick fires when clicked", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Clickable</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("does not fire onClick when disabled", () => {
    const handleClick = vi.fn();
    render(
      <Button disabled onClick={handleClick}>
        Disabled
      </Button>
    );
    const btn = screen.getByRole("button");
    fireEvent.click(btn);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("sm size applies correct min-height class", () => {
    render(<Button size="sm">Small</Button>);
    expect(screen.getByRole("button").className).toContain("min-h-[40px]");
  });

  it("md size applies correct min-height class", () => {
    render(<Button size="md">Medium</Button>);
    expect(screen.getByRole("button").className).toContain("min-h-[56px]");
  });

  it("lg size applies correct min-height class", () => {
    render(<Button size="lg">Large</Button>);
    expect(screen.getByRole("button").className).toContain("min-h-[64px]");
  });
});
