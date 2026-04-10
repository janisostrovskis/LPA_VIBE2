"use client";

import React, { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  titleId?: string;
  children: React.ReactNode;
  className?: string;
}

function getFocusableElements(container: HTMLElement): HTMLElement[] {
  return Array.from(
    container.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
    )
  ).filter((el) => !el.hasAttribute("disabled") && el.tabIndex !== -1);
}

export default function Modal({
  open,
  onClose,
  title,
  titleId: titleIdProp,
  children,
  className = "",
}: ModalProps) {
  const generatedId = useId();
  const titleId = titleIdProp ?? `modal-title-${generatedId}`;

  const cardRef = useRef<HTMLDivElement>(null);
  // Track the element that had focus before the modal opened
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // ESC key handler + focus management
  useEffect(() => {
    if (!open) return;

    previousFocusRef.current = document.activeElement as HTMLElement;

    // Focus the first focusable element inside the card
    const frame = requestAnimationFrame(() => {
      if (!cardRef.current) return;
      const focusable = getFocusableElements(cardRef.current);
      const firstFocusable = focusable[0];
      if (firstFocusable) {
        firstFocusable.focus();
      } else {
        cardRef.current.focus();
      }
    });

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      // Tab trap: cycle focus within the modal
      if (e.key === "Tab" && cardRef.current) {
        const focusable = getFocusableElements(cardRef.current);
        if (focusable.length === 0) return;
        const first = focusable[0] as HTMLElement | undefined;
        const last = focusable[focusable.length - 1] as HTMLElement | undefined;
        if (!first || !last) return;
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      cancelAnimationFrame(frame);
      document.removeEventListener("keydown", handleKeyDown);
      // Return focus to the previous element on cleanup (close)
      previousFocusRef.current?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  const overlay = (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-lpa-surface/80 backdrop-blur-modal"
      onClick={onClose}
    >
      <div
        ref={cardRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className={`bg-lpa-surface-container-lowest rounded-card-md p-lpa-l shadow-cloud-lift max-w-[min(560px,92vw)] w-full focus-visible:outline-none ${className}`}
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id={titleId}
          className="font-headline text-headline-md text-lpa-on-surface mb-lpa-s"
        >
          {title}
        </h2>
        {children}
      </div>
    </div>
  );

  return createPortal(overlay, document.body);
}
