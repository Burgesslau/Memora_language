"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Header } from "@/components/layout/header";
import { EvaluationResult } from "@/components/grammar/evaluation-result";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useGrammarEvaluation } from "@/hooks/useGrammarEvaluation";
import { KnowledgeGraphView } from "@/components/graph/knowledge-graph-view";

const EXAM_PROMPTS = [
  {
    text: "用第三人称单数描述：He _____ (go) to school every day.",
    grammar_point: "third_person_singular",
    star_level: 2,
    hint: "goes",
  },
  {
    text: "完成句子：She has _____ (study) English for three years.",
    grammar_point: "present_perfect",
    star_level: 3,
    hint: "studied",
  },
];

export default function ExamModePage() {
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [timeLeft, setTimeLeft] = useState(120);
  const [mastery, setMastery] = useState(65);
  const { speakMutation, diagnoseMutation } = useGrammarEvaluation();

  const prompt = EXAM_PROMPTS[index];

  useEffect(() => {
    if (timeLeft <= 0) return;
    const t = setInterval(() => setTimeLeft((s) => s - 1), 1000);
    return () => clearInterval(t);
  }, [timeLeft]);

  const handleSubmit = async () => {
    const fullSentence = prompt.text.replace("_____", answer || "___");
    const res = await speakMutation.mutateAsync({ text: fullSentence, mode: "strict" });
    setMastery((m) => (res.data.passed ? m + 5 : m - 7));
    if (!res.data.passed) {
      diagnoseMutation.mutate(prompt.grammar_point);
    }
  };

  return (
    <>
      <Header title="严谨应试模式" subtitle="高压、精准、闭环" />
      <div className="flex flex-1 overflow-hidden">
        <div className="flex flex-1 flex-col p-8">
          <div className="mb-6 flex items-center justify-between">
            <motion.div
              animate={{ color: timeLeft < 30 ? "hsl(var(--error))" : "hsl(var(--text))" }}
              className="text-heading font-mono font-bold"
            >
              {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
            </motion.div>
            <div className="flex gap-2">
              <Badge variant="warning">{"★".repeat(prompt.star_level)}</Badge>
              <Badge variant="outline">{prompt.grammar_point}</Badge>
            </div>
          </div>

          <Card className="mb-6">
            <CardContent className="p-6">
              <p className="text-subtitle">{prompt.text}</p>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Input
              placeholder="填入答案..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
            />
            <Button onClick={handleSubmit} disabled={speakMutation.isPending}>
              提交
            </Button>
          </div>

          {speakMutation.data && (
            <div className="mt-6">
              <EvaluationResult result={speakMutation.data.data} />
            </div>
          )}

          <div className="mt-4 flex items-center gap-3 text-sm">
            <span>掌握率变化：</span>
            <motion.span
              key={mastery}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              className="font-semibold text-[hsl(var(--accent))]"
            >
              {mastery}%
            </motion.span>
          </div>
        </div>

        <div className="w-[420px] border-l border-[hsl(var(--border))] p-4">
          <p className="mb-2 text-sm font-medium">图谱联动</p>
          <div className="h-[400px] overflow-hidden rounded-[var(--radius-lg)]">
            <KnowledgeGraphView />
          </div>
          {diagnoseMutation.data?.data.is_bottleneck && (
            <p className="mt-3 text-sm text-[hsl(var(--warning))]">
              {diagnoseMutation.data.data.recommendation}
            </p>
          )}
        </div>
      </div>
    </>
  );
}
