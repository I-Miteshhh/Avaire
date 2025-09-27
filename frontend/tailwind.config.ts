import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx,mdx}",
    "./components/**/*.{ts,tsx,mdx}",
    "./lib/**/*.{ts,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#f97316",
          soft: "#fed7aa",
          dark: "#ea580c"
        }
      },
      boxShadow: {
        glow: "0 25px 60px -25px rgba(249, 115, 22, 0.45)"
      }
    }
  },
  plugins: []
};

export default config;
