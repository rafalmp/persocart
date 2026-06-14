import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
}

const variantClass: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary: "bg-primary text-white hover:bg-primary-dark",
  secondary:
    "bg-surface border border-border text-text-primary hover:bg-border/40",
  danger: "bg-error text-white hover:opacity-90",
  ghost: "text-text-secondary hover:text-text-primary hover:bg-surface",
};

const sizeClass: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      className={[
        "inline-flex items-center gap-1.5 rounded-md font-medium transition-colors",
        "min-h-[44px] focus-visible:outline-2 focus-visible:outline-focus-ring",
        variantClass[variant],
        sizeClass[size],
        disabled ? "opacity-50 cursor-not-allowed" : "",
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </button>
  );
}
