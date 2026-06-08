"use client";

import { Header } from "@/components/layout/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useUserStore } from "@/stores/useUserStore";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function NotebookPage() {
  const { notebook } = useUserStore();

  const trendData = Object.values(
    notebook.reduce<Record<string, { name: string; count: number }>>((acc, item) => {
      const key = item.error_type;
      if (!acc[key]) acc[key] = { name: key, count: 0 };
      acc[key].count += item.count;
      return acc;
    }, {}),
  );

  return (
    <>
      <Header title="错题本" subtitle="高频错误与趋势分析" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>错题列表</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {notebook.length === 0 ? (
                <p className="text-sm text-[hsl(var(--muted))]">暂无错题记录</p>
              ) : (
                notebook.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-start justify-between rounded-[var(--radius-md)] border border-[hsl(var(--border))] p-4"
                  >
                    <div>
                      <div className="flex gap-2">
                        <Badge variant="error">{item.error_type}</Badge>
                        <Badge variant="outline">{item.mode}</Badge>
                      </div>
                      <p className="mt-2 font-medium">{item.label}</p>
                      <p className="mt-1 text-sm text-[hsl(var(--muted))]">{item.message}</p>
                    </div>
                    <span className="text-sm text-[hsl(var(--muted))]">×{item.count}</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>错误趋势</CardTitle></CardHeader>
            <CardContent className="h-72">
              {trendData.length === 0 ? (
                <p className="text-sm text-[hsl(var(--muted))]">完成练习后生成趋势</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trendData}>
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="hsl(var(--error))" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
