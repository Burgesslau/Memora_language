"use client";

import { Header } from "@/components/layout/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GRAPH_NODES } from "@/services/graph-data";
import { KnowledgeGraphView } from "@/components/graph/knowledge-graph-view";
import { masteryToColor, formatPercent } from "@/lib/utils";

export default function GrammarDashboardPage() {
  const nodes = GRAPH_NODES.filter((n) => n.node_type === "grammar");

  return (
    <>
      <Header title="语法仪表盘" subtitle="按语法点查看掌握度与诊断入口" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>语法点概览</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {nodes.map((n) => (
                  <div key={n.id} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{n.label}</div>
                        <div className="text-xs text-[hsl(var(--muted))]">{n.description}</div>
                      </div>
                      <div className="text-sm font-semibold">{formatPercent(n.mastery_score)}</div>
                    </div>

                    <div className="h-2 w-full rounded-full bg-[hsl(var(--muted)/0.12)]">
                      <div
                        className="h-2 rounded-full"
                        style={{ width: `${n.mastery_score}%`, background: masteryToColor(n.mastery_score) }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>快速操作</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[hsl(var(--muted))]">点击知识图谱中的节点可查看详情并发起诊断。</p>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <KnowledgeGraphView />
          </div>
        </div>
      </div>
    </>
  );
}
