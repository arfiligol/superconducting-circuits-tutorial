"use client";

import { useSyncExternalStore } from "react";

import { useTheme } from "next-themes";

const themeOrder = ["light", "dark", "system"] as const;
const noopSubscribe = () => () => undefined;

export function ThemeToggle() {
  const { resolvedTheme, setTheme, theme } = useTheme();
  const mounted = useSyncExternalStore(noopSubscribe, () => true, () => false);

  const currentTheme = themeOrder.includes((theme ?? "system") as (typeof themeOrder)[number])
    ? (theme as (typeof themeOrder)[number])
    : "system";

  function cycleTheme() {
    const currentIndex = themeOrder.indexOf(currentTheme);
    const nextTheme = themeOrder[(currentIndex + 1) % themeOrder.length];
    setTheme(nextTheme);
  }

  return (
    <button
      type="button"
      onClick={cycleTheme}
      className="rounded-full border border-border bg-card px-3 py-1.5 text-sm text-card-foreground transition hover:border-primary hover:text-primary"
    >
      Theme: {mounted ? resolvedTheme ?? currentTheme : "system"}
    </button>
  );
}
