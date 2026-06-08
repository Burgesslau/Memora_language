"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Header } from "@/components/layout/header";
import { MicButton } from "@/components/speech/mic-button";
import { LiveTranscript } from "@/components/speech/live-transcript";
import { EvaluationResult } from "@/components/grammar/evaluation-result";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { useGrammarEvaluation } from "@/hooks/useGrammarEvaluation";
import { useAudioStore } from "@/stores/useAudioStore";

export default function FreeModePage() {
  const [manualText, setManualText] = useState("");
  const [showResult, setShowResult] = useState(false);
  const { start, stop, supported } = useSpeechRecognition();
  const { transcript, reset: resetAudio } = useAudioStore();
  const { speakMutation } = useGrammarEvaluation();

  const handleSubmit = async (text: string) => {
    if (!text.trim()) return;
    await speakMutation.mutateAsync({ text: text.trim(), mode: "free" });
    setShowResult(true);
  };

  const handleStopAndEvaluate = () => {
    stop();
    if (transcript.trim()) handleSubmit(transcript);
  };

  return (
    <>
      <Header
        title="自由表达模式"
        subtitle="保护表达欲 — 说话过程中不会被打断"
      />
      <div className="flex flex-1">
        <div className="flex flex-1 flex-col items-center justify-center gap-8 p-8">
          <MicButton
            onStart={() => { resetAudio(); start(); }}
            onStop={handleStopAndEvaluate}
            disabled={!supported}
          />
          {!supported && (
            <p className="text-sm text-[hsl(var(--warning))]">
              当前浏览器不支持 Web Speech API，请使用文字输入
            </p>
          )}
          <LiveTranscript />

          <div className="flex w-full max-w-md gap-2">
            <Input
              placeholder="或直接输入英文句子..."
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit(manualText)}
            />
            <Button
              onClick={() => handleSubmit(manualText || transcript)}
              disabled={speakMutation.isPending}
            >
              {speakMutation.isPending ? "分析中..." : "结束并分析"}
            </Button>
          </div>
        </div>

        <AnimatePresence>
          {showResult && speakMutation.data && (
            <motion.div
              initial={{ x: 400 }}
              animate={{ x: 0 }}
              exit={{ x: 400 }}
              className="w-96 border-l border-[hsl(var(--border))] p-6"
            >
              <EvaluationResult result={speakMutation.data.data} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
