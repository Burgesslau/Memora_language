"use client";

import { useThemeStore } from "@/stores/useThemeStore";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/** HSL 动态主题轮盘 */
export function ThemeWheel() {
  const { hue, saturation, lightness, setWheel } = useThemeStore();

  return (
    <Card>
      <CardHeader>
        <CardTitle>RGB 主题轮盘</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <Slider label="Hue 色相" value={hue} min={0} max={360} onChange={(v) => setWheel(v, saturation, lightness)} />
        <Slider label="Saturation 饱和度" value={saturation} min={0} max={100} onChange={(v) => setWheel(hue, v, lightness)} />
        <Slider label="Lightness 亮度" value={lightness} min={20} max={80} onChange={(v) => setWheel(hue, saturation, v)} />
        <div
          className="h-16 rounded-[var(--radius-lg)]"
          style={{ backgroundColor: `hsl(${hue} ${saturation}% ${lightness}%)` }}
        />
      </CardContent>
    </Card>
  );
}
