"use client";

import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  const { theme, setTheme } = useTheme();

  return (
    <header className="flex items-center justify-between border-b border-[hsl(var(--border))] px-8 py-5">
      <div>
        <h1 className="text-hero font-semibold">{title}</h1>
        {subtitle && (
          <p className="mt-1 text-sm text-[hsl(var(--muted))]">{subtitle}</p>
        )}
      </div>
      <Button
        variant="outline"
        size="icon"
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        aria-label="切换主题"
      >
        <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      </Button>
    </header>
  );
}
