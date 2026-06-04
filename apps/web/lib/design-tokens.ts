/**
 * CV Master Design Tokens
 * Single source of truth for all visual values.
 * Used by globals.css and referenced by components via Tailwind classes.
 */

export const tokens = {
  color: {
    // Surfaces
    page: "slate-950",
    surface: "slate-900",
    surfaceHover: "slate-800",
    border: "slate-700",
    borderSubtle: "slate-800",

    // Text
    text: "slate-100",
    textSecondary: "slate-300",
    textMuted: "slate-400",
    textPlaceholder: "slate-500",

    // Accent
    accent: "blue-500",
    accentHover: "blue-400",
    accentBg: "blue-950",
    accentText: "blue-300",

    // Semantic
    success: "emerald-400",
    successBg: "emerald-950",
    successBorder: "emerald-800",
    error: "red-400",
    errorBg: "red-950",
    errorBorder: "red-800",
    warning: "amber-400",
    warningBg: "amber-950",
    warningBorder: "amber-800",
  },

  spacing: {
    pageSection: "space-y-8",
    cardPadding: "p-6",
    cardGap: "gap-4",
    formGap: "gap-3",
  },

  radius: {
    sm: "rounded",
    md: "rounded-md",
    lg: "rounded-lg",
    xl: "rounded-xl",
  },

  shadow: {
    card: "shadow-sm",
    modal: "shadow-md",
  },

  type: {
    pageTitle: "text-2xl font-bold",
    pageDesc: "text-slate-400 mt-1",
    cardTitle: "font-semibold",
    body: "text-sm",
    meta: "text-xs",
  },
} as const;
