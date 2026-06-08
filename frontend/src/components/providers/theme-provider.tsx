"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import { ReactNode, useEffect } from "react";
import { useThemeStore } from "@/stores/useThemeStore";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const applyToDocument = useThemeStore((s) => s.applyToDocument);

  useEffect(() => {
    applyToDocument();
  }, [applyToDocument]);

  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  );
}
