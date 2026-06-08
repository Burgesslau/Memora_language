import { AppShell } from "@/components/layout/app-shell";

export default function NotebookLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
