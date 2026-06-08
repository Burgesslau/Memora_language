import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "destructive";
  size?: "sm" | "md" | "lg" | "icon";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "md", ...props }, ref) => {
    const variants = {
      default: "bg-[hsl(var(--accent))] text-white hover:bg-[hsl(var(--accent-hover))]",
      outline: "border border-[hsl(var(--border))] bg-transparent hover:bg-[hsl(var(--card))]",
      ghost: "bg-transparent hover:bg-[hsl(var(--card))]",
      destructive: "bg-[hsl(var(--error))] text-white hover:opacity-90",
    };
    const sizes = {
      sm: "h-8 px-3 text-sm rounded-[var(--radius-sm)]",
      md: "h-10 px-4 text-sm rounded-[var(--radius-md)]",
      lg: "h-12 px-6 text-base rounded-[var(--radius-md)]",
      icon: "h-10 w-10 rounded-[var(--radius-md)]",
    };
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-colors disabled:opacity-50",
          variants[variant],
          sizes[size],
          className,
        )}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";
