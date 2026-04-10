import React from "react";

export type ButtonVariant = "primary" | "secondary" | "text";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  type?: "button" | "submit" | "reset";
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-gradient-to-br from-lpa-primary to-lpa-primary-container text-lpa-on-primary " +
    "hover:shadow-cloud active:scale-[0.98]",
  secondary:
    "bg-lpa-secondary-container text-lpa-on-secondary-container " +
    "hover:bg-lpa-secondary-fixed",
  text:
    "bg-transparent text-lpa-primary hover:underline hover:text-lpa-secondary",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "min-h-[40px] px-4 text-label-sm",
  md: "min-h-[56px] px-8 text-label-md",
  lg: "min-h-[64px] px-10 text-label-md",
};

export default function Button({
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  type = "button",
  onClick,
  children,
  className = "",
}: ButtonProps): React.JSX.Element {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading ? "true" : undefined}
      onClick={onClick}
      className={[
        "inline-flex items-center justify-center rounded-pill",
        "font-label uppercase tracking-[0.1em]",
        "transition-all duration-200 ease-out",
        "focus-visible:outline focus-visible:outline-2",
        "focus-visible:outline-lpa-secondary focus-visible:outline-offset-[3px]",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
        variantClasses[variant],
        sizeClasses[size],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      )}
      {children}
    </button>
  );
}
