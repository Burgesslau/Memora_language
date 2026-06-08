"use client";

import { Flame, MessageSquare, Clock, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { Header } from "@/components/layout/header";
import { KpiCard } from "@/components/shared/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useUserStore } from "@/stores/useUserStore";
import { GRAPH_NODES } from "@/services/graph-data";
import { formatPercent, masteryToColor } from "@/lib/utils";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export default function DashboardPage() {
  const { stats, notebook } = useUserStore();

  const competenceData = GRAPH_NODES.slice(0, 6).map((n) => ({
    name: n.label,
    score: n.mastery_score,
  }));

  const topVulnerabilities = [...notebook]
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  return (
    <>
      <Header
        title="学习仪表盘"
        subtitle="英语能力导航系统 — 我现在在哪？下一步学什么？"
      />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard title="连续学习天数" value={stats.streakDays} subtitle="保持心流" icon={Flame} highlight />
          <KpiCard title="今日输出句数" value={stats.todayOutputCount} subtitle="主动产出" icon={MessageSquare} />
          <KpiCard title="今日学习时长" value={`${stats.todayMinutes} min`} icon={Clock} />
          <KpiCard title="待修复漏洞" value={notebook.length} icon={AlertTriangle} />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>能力总览</CardTitle>
            </CardHeader>
            <CardContent className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={competenceData}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(v: number) => formatPercent(v)} />
                  <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                    {competenceData.map((entry, i) => (
                      <Cell key={i} fill={masteryToColor(entry.score)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>今日漏洞</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {topVulnerabilities.length === 0 ? (
                <p className="text-sm text-[hsl(var(--muted))]">暂无记录，开始练习吧！</p>
              ) : (
                topVulnerabilities.map((v) => (
                  <div key={v.id} className="flex items-center justify-between text-sm">
                    <div>
                      <Badge variant="error">{v.error_type}</Badge>
                      <p className="mt-1">{v.label}</p>
                    </div>
                    <span className="text-[hsl(var(--muted))]">×{v.count}</span>
                  </div>
                ))
              )}
              {topVulnerabilities.length > 0 && (
                <Link href="/practice/exam">
                  <Button variant="outline" className="w-full">微训练</Button>
                </Link>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>快速开始</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-4">
            <Link href="/practice/free"><Button>自由表达</Button></Link>
            <Link href="/practice/exam"><Button variant="outline">严谨应试</Button></Link>
            <Link href="/practice/talk"><Button variant="outline">口语练兵场</Button></Link>
            <Link href="/graph"><Button variant="ghost">查看知识图谱</Button></Link>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
