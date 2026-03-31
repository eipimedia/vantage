import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0A0A0F",
        card: "#13131A",
        border: "#1E1E2E",
        accent: "#0EA5E9",
        "accent-dark": "#0284C7",
        muted: "#94A3B8",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
