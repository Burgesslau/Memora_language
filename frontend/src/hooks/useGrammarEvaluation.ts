"use client";

import { useMutation } from "@tanstack/react-query";
import { evaluateSpeech, diagnoseBottleneck } from "@/services/api";
import type { EvaluationMode, SpeakRequest } from "@/types/api";
import { useUserStore } from "@/stores/useUserStore";

/** 封装 speak + diagnose 的 React Query Hook */
export function useGrammarEvaluation() {
  const { userId, recordResult, failureCounts } = useUserStore();

  const speakMutation = useMutation({
    mutationFn: (params: { text: string; mode: EvaluationMode }) => {
      const payload: SpeakRequest = {
        user_text: params.text,
        mode: params.mode,
        user_id: userId,
      };
      return evaluateSpeech(payload);
    },
    onSuccess: (res) => {
      recordResult(res.data);
    },
  });

  const diagnoseMutation = useMutation({
    mutationFn: (grammarPoint: string) =>
      diagnoseBottleneck({
        user_id: userId,
        grammar_point: grammarPoint,
        consecutive_failures: failureCounts[grammarPoint] ?? 0,
      }),
  });

  return { speakMutation, diagnoseMutation, failureCounts };
}
