"use client";

import type { ParseOutputResponse } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { InlineHighlight } from "./inline-highlight";

interface EvaluationResultProps {
  result: ParseOutputResponse;
}

/** 解析结果展示面板 */
export function EvaluationResult({ result }: EvaluationResultProps) {
  const errors = result.mode === "free" ? result.silent_errors : result.error_tags;

  return (
    <Card className="shadow-medium">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>诊断结果</CardTitle>
          <Badge variant={result.passed ? "success" : "error"}>
            {result.passed ? "通过" : "未通过"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-[hsl(var(--muted))]">{result.feedback}</p>

        {result.mode === "strict" ? (
          <InlineHighlight text={result.user_text} errorTags={result.error_tags} />
        ) : (
          <p className="text-base">{result.user_text}</p>
        )}

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-[var(--radius-md)] bg-[hsl(var(--background))] p-3">
            <p className="text-[hsl(var(--muted))]">结构评分</p>
            <p className="text-heading font-semibold">
              {Math.round(result.core_structure.structure_score * 100)}%
            </p>
          </div>
          <div className="rounded-[var(--radius-md)] bg-[hsl(var(--background))] p-3">
            <p className="text-[hsl(var(--muted))]">发现问题</p>
            <p className="text-heading font-semibold">{errors.length}</p>
          </div>
        </div>

        {result.mode === "free" && result.silent_errors.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">静默记录（不影响通过）</p>
            {result.silent_errors.map((e, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-[hsl(var(--muted))]">
                <Badge variant="outline">{e.error_type}</Badge>
                <span>{e.message}</span>
              </div>
            ))}
          </div>
        )}

        {result.mode === "strict" && result.error_tags.length > 0 && (
          <div className="space-y-2">
            {result.error_tags.map((e, i) => (
              <div key={i} className="flex flex-wrap items-center gap-2 text-sm">
                <Badge variant="error">{e.grammar_point}</Badge>
                <Badge variant="warning">{"★".repeat(e.star_level)}</Badge>
                <span>{e.message}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
