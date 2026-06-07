import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: {
        "2xl": "1100px",
      },
    },
    extend: {
      colors: {
        // ── design tokens from standalone.html :root ──
        bg: "hsl(var(--bg))",
        surface: "hsl(var(--surface))",
        "surface-accent": "hsl(var(--surface-accent))",
        "surface-muted": "hsl(var(--surface-muted))",
        border: "hsl(var(--border))",
        text: "hsl(var(--text))",
        muted: "hsl(var(--muted))",
        info: "hsl(var(--info))",
        link: "hsl(var(--link))",

        // semantic — shadcn-aligned
        danger: {
          bg: "hsl(var(--danger-bg))",
          fg: "hsl(var(--danger-fg))",
        },
        success: {
          bg: "hsl(var(--success-bg))",
          fg: "hsl(var(--success-fg))",
        },
        warning: {
          bg: "hsl(var(--warning-bg))",
          fg: "hsl(var(--warning-fg))",
        },

        // shadcn default token map (re-mapped onto our palette)
        background: "hsl(var(--bg))",
        foreground: "hsl(var(--text))",
        card: {
          DEFAULT: "hsl(var(--surface))",
          foreground: "hsl(var(--text))",
        },
        popover: {
          DEFAULT: "hsl(var(--surface))",
          foreground: "hsl(var(--text))",
        },
        primary: {
          DEFAULT: "hsl(var(--info))",
          foreground: "#ffffff",
        },
        secondary: {
          DEFAULT: "hsl(var(--surface-muted))",
          foreground: "hsl(var(--text))",
        },
        accent: {
          DEFAULT: "hsl(var(--surface-muted))",
          foreground: "hsl(var(--text))",
        },
        destructive: {
          DEFAULT: "hsl(var(--danger-fg))",
          foreground: "#ffffff",
        },
        input: "hsl(var(--border))",
        ring: "hsl(var(--info))",
        radius: {
          lg: "var(--radius-lg)",
          md: "8px",
          sm: "6px",
        },
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
      fontVariantNumeric: {
        tabular: "tabular-nums",
      },
      borderWidth: {
        DEFAULT: "0.5px",
        "0.5": "0.5px",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
