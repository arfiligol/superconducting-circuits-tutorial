"use client";

import { useSyncExternalStore } from "react";

import { Laptop, MoonStar, SunMedium } from "lucide-react";
import { useTheme } from "next-themes";

const themeOrder = ["light", "dark", "system"] as const;
const noopSubscribe = () => () => undefined;

type ThemeToggleProps = Readonly<{
  className?: string;
}>;

export function ThemeToggle({ className }: ThemeToggleProps) {
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

  const effectiveTheme = mounted ? currentTheme : "dark";
  const displayTheme = mounted ? resolvedTheme ?? currentTheme : "dark";
  const Icon = effectiveTheme === "light" ? SunMedium : effectiveTheme === "dark" ? MoonStar : Laptop;
  const nextTheme = themeOrder[(themeOrder.indexOf(effectiveTheme) + 1) % themeOrder.length];

  return (
    <button
      type="button"
      onClick={cycleTheme}
      className={[
        "inline-flex h-10 w-10 items-center justify-center rounded-full text-primary transition hover:bg-surface-elevated hover:text-primary-foreground",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      aria-label={`Theme: ${displayTheme}. Switch to ${nextTheme}.`}
      title={`Theme: ${displayTheme}. Switch to ${nextTheme}.`}
    >
      <Icon size={18} strokeWidth={2} />
    </button>
  );
}
