"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { BottleneckDiagnosis } from "@/types/api";
import type { GraphNodeData } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatPercent } from "@/lib/utils";
import Link from "next/link";

interface DetailPanelProps {
  node: GraphNodeData | null;
  diagnosis?: BottleneckDiagnosis | null;
  onClose: () => void;
  onDiagnose?: () => void;
  diagnosing?: boolean;
}

/** 图谱右侧详情抽屉 */
export function DetailPanel({
  node,
  diagnosis,
  onClose,
  onDiagnose,
  diagnosing,
}: DetailPanelProps) {
  return (
    <AnimatePresence>
      {node && (
        <motion.aside
          initial={{ x: 320, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 320, opacity: 0 }}
          className="absolute right-0 top-0 z-10 h-full w-80 border-l border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-floating"
        >
          <div className="mb-4 flex items-start justify-between">
            <div>
              <h3 className="text-heading font-semibold">{node.label}</h3>
              <p className="mt-1 text-sm text-[hsl(var(--muted))]">{node.id}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>关闭</Button>
          </div>

          <p className="text-sm leading-relaxed">{node.description}</p>

          <div className="mt-6 space-y-3">
            <div className="rounded-[var(--radius-md)] bg-[hsl(var(--background))] p-4">
              <p className="text-sm text-[hsl(var(--muted))]">掌握率</p>
              <p className="text-display text-[hsl(var(--accent))]">
                {formatPercent(node.mastery_score)}
              </p>
            </div>

            {onDiagnose && (
              <Button className="w-full" onClick={onDiagnose} disabled={diagnosing}>
                {diagnosing ? "诊断中..." : "瓶颈逆向诊断"}
              </Button>
            )}

            {diagnosis?.is_bottleneck && (
              <div className="space-y-3 rounded-[var(--radius-md)] border border-[hsl(var(--warning)/0.3)] p-4">
                <Badge variant="warning">瓶颈触发</Badge>
                <p className="text-sm">{diagnosis.recommendation}</p>
                <div className="space-y-2">
                  <p className="text-sm font-medium">前置依赖</p>
                  {diagnosis.prerequisite_nodes.map((p) => (
                    <div key={p.node_id} className="text-sm text-[hsl(var(--muted))]">
                      <Badge variant="outline">深度 {p.depth}</Badge> {p.label}
                    </div>
                  ))}
                </div>
                {diagnosis.micro_drill_ids.length > 0 && (
                  <Link href="/practice/exam">
                    <Button variant="outline" className="w-full">
                      开始微操练 ({diagnosis.micro_drill_ids.length})
                    </Button>
                  </Link>
                )}
              </div>
            )}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
