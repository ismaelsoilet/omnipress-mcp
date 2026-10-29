import React from "react";

/**
 * Universal video theme.
 *
 * Every composition is channel-agnostic: colors arrive via props (or a
 * `theme` object) and are exposed as CSS custom properties. Components never
 * hardcode a brand color; they consume `var(--omni-*)` with neutral fallbacks.
 */
export interface VideoTheme {
  primary: string;
  accent: string;
  highlight: string;
  background: string;
  text: string;
  secondaryText: string;
  success: string;
  danger: string;
}

export const DEFAULT_THEME: VideoTheme = {
  primary: "#3B82F6",
  accent: "#3B82F6",
  highlight: "#FACC15",
  background: "#0B1220",
  text: "#FFFFFF",
  secondaryText: "#94A3B8",
  success: "#10B981",
  danger: "#EF4444",
};

export const resolveTheme = (partial?: Partial<VideoTheme>): VideoTheme => ({
  ...DEFAULT_THEME,
  ...(partial || {}),
});

const normalizeHex = (hex: string): string => {
  const raw = (hex || "").replace("#", "").trim();
  if (raw.length === 3) {
    return raw
      .split("")
      .map((char) => char + char)
      .join("");
  }
  return raw;
};

export const hexToRgbTriplet = (hex: string, fallback = "59, 130, 246"): string => {
  const raw = normalizeHex(hex);
  if (!/^[0-9a-fA-F]{6}$/.test(raw)) {
    return fallback;
  }
  return `${parseInt(raw.slice(0, 2), 16)}, ${parseInt(raw.slice(2, 4), 16)}, ${parseInt(
    raw.slice(4, 6),
    16,
  )}`;
};

export interface ThemeVarsInput {
  primaryColor?: string;
  accentColor?: string;
  highlightColor?: string;
  backgroundColor?: string;
  textColor?: string;
  secondaryTextColor?: string;
  successColor?: string;
  dangerColor?: string;
}

export const themeVars = (input: ThemeVarsInput = {}): React.CSSProperties => {
  const theme = resolveTheme({
    primary: input.primaryColor,
    accent: input.accentColor || input.primaryColor,
    highlight: input.highlightColor,
    background: input.backgroundColor,
    text: input.textColor,
    secondaryText: input.secondaryTextColor,
    success: input.successColor,
    danger: input.dangerColor,
  });

  return {
    ["--omni-primary" as string]: theme.primary,
    ["--omni-primary-rgb" as string]: hexToRgbTriplet(theme.primary),
    ["--omni-accent" as string]: theme.accent,
    ["--omni-accent-rgb" as string]: hexToRgbTriplet(theme.accent),
    ["--omni-highlight" as string]: theme.highlight,
    ["--omni-highlight-rgb" as string]: hexToRgbTriplet(theme.highlight, "250, 204, 21"),
    ["--omni-background" as string]: theme.background,
    ["--omni-background-rgb" as string]: hexToRgbTriplet(theme.background, "11, 18, 32"),
    ["--omni-text" as string]: theme.text,
    ["--omni-secondary-text" as string]: theme.secondaryText,
    ["--omni-success" as string]: theme.success,
    ["--omni-success-rgb" as string]: hexToRgbTriplet(theme.success, "16, 185, 129"),
    ["--omni-danger" as string]: theme.danger,
    ["--omni-danger-rgb" as string]: hexToRgbTriplet(theme.danger, "239, 68, 68"),
  } as React.CSSProperties;
};
