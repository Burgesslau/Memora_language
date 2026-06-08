"use client";

import { cn } from "@/lib/utils";

interface SliderProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  label: string;
  onChange: (value: number) => void;
  className?: string;
}

export function Slider({ value, min, max, step = 1, label, onChange, className }: SliderProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex justify-between text-sm">
        <span className="text-[hsl(var(--muted))]">{label}</span>
        <span className="font-medium">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-[hsl(var(--border))] accent-[hsl(var(--accent))]"
      />
    </div>
  );
}
