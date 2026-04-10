"use client";

import React, { useEffect, useRef } from "react";

export type ToastVariant = "success" | "error" | "info";

export interface ToastProps {
  variant?: ToastVariant;
  message: string;
  duration?: number;
  onDismiss?: () => void;
  visible: boolean;
}

const variantTextClass: Record<ToastVariant, string> = {
  success: "text-lpa-secondary",
  error:   "text-[#B64949]",
  info:    "text-lpa-tertiary",
};

const variantBorderClass: Record<ToastVariant, string> = {
  success: "border-l-4 border-lpa-secondary",
  error:   "border-l-4 border-[#B64949]",
  info:    "border-l-4 border-lpa-tertiary",
};

export default function Toast({
  variant = "info",
  message,
  duration = 5000,
  onDismiss,
  visible,
}: ToastProps) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!visible) {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      return;
    }
    timerRef.current = setTimeout(() => {
      onDismiss?.();
    }, duration);
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [visible, duration, onDismiss]);

  if (!visible) return null;

  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      aria-live={variant === "error" ? "assertive" : "polite"}
      className={[
        "fixed top-4 right-4 z-[300]",
        "bg-lpa-surface-container-highest/80 backdrop-blur-nav",
        "rounded-pill px-6 py-3 shadow-cloud",
        "font-body text-body-md text-lpa-on-surface",
        "transition-opacity duration-300",
        variantBorderClass[variant],
      ].join(" ")}
    >
      <span className={variantTextClass[variant]}>{message}</span>
    </div>
  );
}
