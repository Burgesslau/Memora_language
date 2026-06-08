"use client";

import { motion } from "framer-motion";
import { Mic, Square } from "lucide-react";
import { useAudioStore } from "@/stores/useAudioStore";
import { cn } from "@/lib/utils";

interface MicButtonProps {
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

/** 自由表达模式：呼吸灯麦克风按钮 */
export function MicButton({ onStart, onStop, disabled }: MicButtonProps) {
  const { isRecording, volumeLevel } = useAudioStore();
  const scale = isRecording ? 1 + volumeLevel * 0.3 : 1;

  return (
    <motion.button
      type="button"
      disabled={disabled}
      onClick={isRecording ? onStop : onStart}
      animate={{ scale }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className={cn(
        "relative flex h-32 w-32 items-center justify-center rounded-full",
        "bg-[hsl(var(--accent))] text-white shadow-floating",
        "disabled:opacity-50",
        isRecording && "ring-4 ring-[hsl(var(--accent)/0.3)]",
      )}
    >
      {isRecording && (
        <motion.span
          className="absolute inset-0 rounded-full bg-[hsl(var(--accent)/0.3)]"
          animate={{ scale: [1, 1.2, 1], opacity: [0.6, 0, 0.6] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
      {isRecording ? <Square className="h-10 w-10" /> : <Mic className="h-10 w-10" />}
    </motion.button>
  );
}
