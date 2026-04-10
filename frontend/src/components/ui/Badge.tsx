import React from "react";

export type BadgeVariant = "primary" | "secondary" | "tertiary" | "outline";

export interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  primary: "bg-lpa-primary-container text-lpa-on-primary-container",
  secondary: "bg-lpa-secondary-container text-lpa-on-secondary-container",
  tertiary: "bg-lpa-tertiary-container text-lpa-on-tertiary-container",
  outline:
    "bg-transparent border border-lpa-outline text-lpa-on-surface",
};

export default function Badge({
  variant = "secondary",
  children,
  className = "",
}: BadgeProps): React.JSX.Element {
  return (
    <span
      className={[
        "rounded-pill px-3 py-1.5 font-label text-label-md uppercase tracking-[0.05em]",
        "inline-flex items-center",
        variantClasses[variant],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </span>
  );
}
