import React from "react";

export type CardVariant = "base" | "feature";

export interface CardProps {
  variant?: CardVariant;
  hover?: boolean;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<CardVariant, string> = {
  base: "bg-lpa-surface-container-lowest rounded-card p-lpa-m",
  feature: "bg-lpa-surface-container rounded-card-md p-lpa-l",
};

const hoverClasses =
  "hover:-translate-y-0.5 hover:shadow-cloud transition-all duration-300 ease-out";

export default function Card({
  variant = "base",
  hover = false,
  children,
  className = "",
}: CardProps): React.JSX.Element {
  return (
    <div
      className={[
        variantClasses[variant],
        hover ? hoverClasses : "",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </div>
  );
}
