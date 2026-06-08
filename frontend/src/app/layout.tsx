import type { Metadata } from "next";
import { AppProviders } from "@/components/providers/app-providers";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Smart Grammar System",
  description: "输出驱动型自适应英语语法学习系统",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
