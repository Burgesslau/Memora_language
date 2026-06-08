"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Brain,
  Home,
  Mic,
  Network,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "仪表盘", icon: Home },
  { href: "/dashboard/grammar", label: "语法仪表盘", icon: BookOpen },
  { href: "/practice/free", label: "练习中心", icon: Mic },
  { href: "/graph", label: "知识图谱", icon: Network },
  { href: "/notebook", label: "错题本", icon: BookOpen },
  { href: "/settings", label: "设置", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
      <div className="mb-8 flex items-center gap-2 px-2">
        <Brain className="h-7 w-7 text-[hsl(var(--accent))]" />
        <div>
          <p className="text-sm font-semibold">Smart Grammar</p>
          <p className="text-xs text-[hsl(var(--muted))]">英语能力导航系统</p>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/dashboard"
              ? pathname === href
              : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2.5 text-sm transition-colors",
                active
                  ? "bg-[hsl(var(--accent)/0.12)] font-medium text-[hsl(var(--accent))]"
                  : "text-[hsl(var(--muted))] hover:bg-[hsl(var(--background))] hover:text-[hsl(var(--text))]",
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
