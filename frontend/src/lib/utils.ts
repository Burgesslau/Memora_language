import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** 合并 Tailwind 类名，解决冲突 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** 掌握率 → 节点视觉状态 */
export function masteryToStatus(score: number): "critical" | "unstable" | "growing" | "mastered" {
  if (score < 40) return "critical";
  if (score < 70) return "unstable";
  if (score < 90) return "growing";
  return "mastered";
}

/** 掌握率 → CSS 颜色值 */
export function masteryToColor(score: number): string {
  const status = masteryToStatus(score);
  const map = {
    critical: "hsl(var(--error))",
    unstable: "hsl(var(--warning))",
    growing: "hsl(var(--accent))",
    mastered: "hsl(var(--success))",
  };
  return map[status];
}

/** 掌握率 → 节点尺寸倍率 */
export function masteryToScale(score: number): number {
  const status = masteryToStatus(score);
  const map = { critical: 0.8, unstable: 1.0, growing: 1.2, mastered: 1.4 };
  return map[status];
}

/** 格式化百分比 */
export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}
