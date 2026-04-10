import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Modal from "../Modal";

describe("Modal", () => {
  it("renders nothing when open=false", () => {
    const { container } = render(
      <Modal open={false} onClose={vi.fn()} title="Test Modal">
        <p>Content</p>
      </Modal>
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders dialog with title when open=true", () => {
    render(
      <Modal open={true} onClose={vi.fn()} title="Hello Modal">
        <p>Body</p>
      </Modal>
    );
    expect(screen.getByText("Hello Modal")).toBeTruthy();
    expect(screen.getByText("Body")).toBeTruthy();
  });

  it("has role=dialog and aria-modal=true", () => {
    render(
      <Modal open={true} onClose={vi.fn()} title="Accessible Modal">
        <p>Content</p>
      </Modal>
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog.getAttribute("aria-modal")).toBe("true");
  });

  it("aria-labelledby matches title element id", () => {
    render(
      <Modal
        open={true}
        onClose={vi.fn()}
        title="Labelled Modal"
        titleId="my-modal-title"
      >
        <p>Content</p>
      </Modal>
    );
    const dialog = screen.getByRole("dialog");
    const labelledBy = dialog.getAttribute("aria-labelledby");
    expect(labelledBy).toBe("my-modal-title");
    const titleEl = document.getElementById("my-modal-title");
    expect(titleEl?.textContent).toBe("Labelled Modal");
  });

  it("ESC key calls onClose", () => {
    const onClose = vi.fn();
    render(
      <Modal open={true} onClose={onClose} title="ESC Modal">
        <p>Content</p>
      </Modal>
    );
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("click on overlay calls onClose", () => {
    const onClose = vi.fn();
    const { container } = render(
      <Modal open={true} onClose={onClose} title="Click Modal">
        <button>Inside</button>
      </Modal>
    );
    // The overlay is the fixed full-screen backdrop div (parent of the dialog card).
    // Clicking it directly (not on the dialog card) should call onClose.
    const dialog = screen.getByRole("dialog");
    const overlay = dialog.parentElement as HTMLElement;
    expect(overlay).not.toBeNull();
    fireEvent.click(overlay);
    expect(onClose).toHaveBeenCalledTimes(1);
    // Suppress unused container warning
    void container;
  });
});
