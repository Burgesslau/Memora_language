import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  highlight?: boolean;
}

export function KpiCard({ title, value, subtitle, icon: Icon, highlight }: KpiCardProps) {
  return (
    <Card className={cn(highlight && "border-[hsl(var(--accent)/0.3)]")}>
      <CardContent className="flex items-start justify-between p-6">
        <div>
          <p className="text-sm text-[hsl(var(--muted))]">{title}</p>
          <p className={cn("mt-2 font-semibold", highlight ? "text-display text-[hsl(var(--accent))]" : "text-hero")}>
            {value}
          </p>
          {subtitle && <p className="mt-1 text-xs text-[hsl(var(--muted))]">{subtitle}</p>}
        </div>
        <div className="rounded-[var(--radius-md)] bg-[hsl(var(--accent)/0.1)] p-3">
          <Icon className="h-5 w-5 text-[hsl(var(--accent))]" />
        </div>
      </CardContent>
    </Card>
  );
}
