import { AppShell } from "@/components/layout/app-shell";

export default function GraphLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
