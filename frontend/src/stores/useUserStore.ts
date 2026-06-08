import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ErrorNotebookItem, ParseOutputResponse } from "@/types/api";
import { DEFAULT_USER_ID } from "@/services/api";

interface UserStats {
  streakDays: number;
  todayOutputCount: number;
  todayMinutes: number;
}

interface UserState {
  userId: string;
  stats: UserStats;
  recentResults: ParseOutputResponse[];
  notebook: ErrorNotebookItem[];
  failureCounts: Record<string, number>;
  setUserId: (id: string) => void;
  recordResult: (result: ParseOutputResponse) => void;
  incrementFailure: (grammarPoint: string) => number;
  resetFailure: (grammarPoint: string) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      userId: DEFAULT_USER_ID,
      stats: { streakDays: 7, todayOutputCount: 0, todayMinutes: 0 },
      recentResults: [],
      notebook: [],
      failureCounts: {},
      setUserId: (id) => set({ userId: id }),
      recordResult: (result) => {
        const errors = result.mode === "free" ? result.silent_errors : result.error_tags;
        const notebook = [...get().notebook];

        errors.forEach((err, idx) => {
          const existing = notebook.find(
            (n) => n.grammar_point === err.grammar_point && n.error_type === err.error_type,
          );
          if (existing) {
            existing.count += 1;
            existing.occurred_at = new Date().toISOString();
          } else {
            notebook.push({
              id: `${err.grammar_point}-${idx}-${Date.now()}`,
              grammar_point: err.grammar_point,
              label: err.grammar_point.replace(/_/g, " "),
              error_type: err.error_type,
              message: err.message,
              mode: result.mode,
              occurred_at: new Date().toISOString(),
              count: 1,
            });
          }
        });

        set({
          stats: {
            ...get().stats,
            todayOutputCount: get().stats.todayOutputCount + 1,
          },
          recentResults: [result, ...get().recentResults].slice(0, 20),
          notebook,
        });

        if (!result.passed && errors.length > 0) {
          get().incrementFailure(errors[0].grammar_point);
        } else if (result.passed && errors.length === 0) {
          errors.forEach(() => {});
        }
      },
      incrementFailure: (grammarPoint) => {
        const current = (get().failureCounts[grammarPoint] ?? 0) + 1;
        set({ failureCounts: { ...get().failureCounts, [grammarPoint]: current } });
        return current;
      },
      resetFailure: (grammarPoint) => {
        const counts = { ...get().failureCounts };
        delete counts[grammarPoint];
        set({ failureCounts: counts });
      },
    }),
    { name: "sg-user-store" },
  ),
);
