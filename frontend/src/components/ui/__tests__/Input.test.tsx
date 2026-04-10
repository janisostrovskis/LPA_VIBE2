import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Input from "../Input";

describe("Input", () => {
  it("renders with label text", () => {
    render(<Input id="name" label="Full Name" />);
    expect(screen.getByLabelText("Full Name")).toBeTruthy();
    expect(screen.getByText("Full Name")).toBeTruthy();
  });

  it("underline variant has border-b class", () => {
    render(<Input id="u" label="Username" variant="underline" />);
    const input = screen.getByLabelText("Username");
    expect(input.className).toContain("border-b");
  });

  it("filled variant has surface-container-high bg class", () => {
    render(<Input id="f" label="First name" variant="filled" />);
    const input = screen.getByLabelText("First name");
    expect(input.className).toContain("bg-lpa-surface-container-high");
  });

  it("error prop shows error message with correct color and aria-invalid", () => {
    render(<Input id="email" label="Email" error="Invalid email" />);
    const input = screen.getByLabelText("Email");
    expect(input.getAttribute("aria-invalid")).toBe("true");
    const errorEl = screen.getByRole("alert");
    expect(errorEl.textContent).toBe("Invalid email");
    expect(errorEl.className).toContain("text-[#B64949]");
  });

  it("hint prop shows hint text", () => {
    render(<Input id="pw" label="Password" hint="At least 8 characters" />);
    expect(screen.getByText("At least 8 characters")).toBeTruthy();
  });

  it("error takes precedence over hint in aria-describedby", () => {
    render(
      <Input
        id="field"
        label="Field"
        hint="Some hint"
        error="Required"
      />
    );
    const input = screen.getByLabelText("Field");
    expect(input.getAttribute("aria-describedby")).toBe("field-error");
  });

  it("label htmlFor matches input id", () => {
    render(<Input id="myfield" label="My Field" />);
    const label = screen.getByText("My Field") as HTMLLabelElement;
    expect(label.htmlFor).toBe("myfield");
  });
});
