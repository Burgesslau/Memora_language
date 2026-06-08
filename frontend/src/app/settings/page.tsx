"use client";

import { Header } from "@/components/layout/header";
import { ThemeWheel } from "@/components/shared/theme-wheel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useUserStore } from "@/stores/useUserStore";

export default function SettingsPage() {
  const { userId, setUserId, stats } = useUserStore();

  return (
    <>
      <Header title="系统设置" subtitle="主题偏好、学习目标与成就" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="grid max-w-4xl gap-6 lg:grid-cols-2">
          <ThemeWheel />

          <Card>
            <CardHeader><CardTitle>学习目标</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-[hsl(var(--muted))]">用户 ID</label>
                <Input
                  className="mt-1"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="rounded-[var(--radius-md)] bg-[hsl(var(--background))] p-4">
                  <p className="text-[hsl(var(--muted))]">连续天数</p>
                  <p className="text-heading font-semibold">{stats.streakDays}</p>
                </div>
                <div className="rounded-[var(--radius-md)] bg-[hsl(var(--background))] p-4">
                  <p className="text-[hsl(var(--muted))]">今日输出</p>
                  <p className="text-heading font-semibold">{stats.todayOutputCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
