import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "outline";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-[hsl(var(--accent)/0.15)] text-[hsl(var(--accent))]",
    success: "bg-[hsl(var(--success)/0.15)] text-[hsl(var(--success))]",
    warning: "bg-[hsl(var(--warning)/0.15)] text-[hsl(var(--warning))]",
    error: "bg-[hsl(var(--error)/0.15)] text-[hsl(var(--error))]",
    outline: "border border-[hsl(var(--border))] text-[hsl(var(--muted))]",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-[var(--radius-sm)] px-2 py-0.5 text-xs font-medium",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
