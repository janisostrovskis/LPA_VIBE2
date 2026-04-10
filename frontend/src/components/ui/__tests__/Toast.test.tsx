import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import Toast from "../Toast";

describe("Toast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders message text when visible", () => {
    render(<Toast visible={true} message="Saved successfully" />);
    expect(screen.getByText("Saved successfully")).toBeTruthy();
  });

  it("success variant uses role=status", () => {
    render(<Toast visible={true} variant="success" message="Done" />);
    expect(screen.getByRole("status")).toBeTruthy();
  });

  it("error variant uses role=alert", () => {
    render(<Toast visible={true} variant="error" message="Error occurred" />);
    expect(screen.getByRole("alert")).toBeTruthy();
  });

  it("info variant uses role=status", () => {
    render(<Toast visible={true} variant="info" message="Info message" />);
    expect(screen.getByRole("status")).toBeTruthy();
  });

  it("auto-dismiss calls onDismiss after duration", () => {
    const onDismiss = vi.fn();
    render(
      <Toast
        visible={true}
        message="Auto dismiss"
        duration={5000}
        onDismiss={onDismiss}
      />
    );
    expect(onDismiss).not.toHaveBeenCalled();
    vi.advanceTimersByTime(5000);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("does not render when visible=false", () => {
    const { container } = render(
      <Toast visible={false} message="Hidden toast" />
    );
    expect(container.innerHTML).toBe("");
  });

  it("does not call onDismiss before duration elapses", () => {
    const onDismiss = vi.fn();
    render(
      <Toast
        visible={true}
        message="Wait"
        duration={3000}
        onDismiss={onDismiss}
      />
    );
    vi.advanceTimersByTime(2999);
    expect(onDismiss).not.toHaveBeenCalled();
  });
});
