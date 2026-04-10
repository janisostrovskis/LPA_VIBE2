import React from "react";

export type InputVariant = "underline" | "filled";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: InputVariant;
  label: string;
  id: string;
  hint?: string;
  error?: string;
  className?: string;
}

export default function Input({
  variant = "underline",
  label,
  id,
  hint,
  error,
  className = "",
  ...rest
}: InputProps) {
  const hintId = `${id}-hint`;
  const errorId = `${id}-error`;

  // aria-describedby: error takes precedence over hint
  const describedBy = error ? errorId : hint ? hintId : undefined;

  const underlineClasses = [
    "w-full bg-transparent border-0 border-b border-lpa-outline-variant/40",
    "py-3 font-body text-body-md text-lpa-on-surface",
    "placeholder:text-lpa-on-surface-variant",
    "transition-colors duration-200 ease-out",
    "focus-visible:outline-none focus-visible:border-b-2 focus-visible:border-lpa-secondary",
    error ? "border-b-2 border-[#B64949]" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const filledClasses = [
    "w-full bg-lpa-surface-container-high rounded-lg border-0",
    "px-4 pt-4 pb-2 font-body text-body-md text-lpa-on-surface",
    "placeholder:text-lpa-on-surface-variant",
    "focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-0",
    error ? "outline outline-2 outline-[#B64949]" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const inputClasses = variant === "underline" ? underlineClasses : filledClasses;

  return (
    <div className={`flex flex-col ${className}`}>
      <label
        htmlFor={id}
        className="mb-2 font-label text-label-sm text-lpa-on-surface-variant font-medium"
      >
        {label}
      </label>
      <input
        id={id}
        className={inputClasses}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={describedBy}
        {...rest}
      />
      {error && (
        <p
          id={errorId}
          role="alert"
          className="mt-1 text-[#B64949] text-[0.8125rem]"
        >
          {error}
        </p>
      )}
      {!error && hint && (
        <p
          id={hintId}
          className="mt-1 text-lpa-on-surface-variant text-[0.8125rem]"
        >
          {hint}
        </p>
      )}
    </div>
  );
}
