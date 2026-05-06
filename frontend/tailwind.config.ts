import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "rgba(255, 255, 255, 0.1)",
        input: "rgba(255, 255, 255, 0.1)",
        ring: "#ecad29",
        background: "#0a0a0b",
        foreground: "#ffffff",
        primary: {
          DEFAULT: "#ecad29",
          foreground: "#000000",
        },
        secondary: {
          DEFAULT: "#161618",
          foreground: "#ffffff",
        },
        card: {
          DEFAULT: "rgba(22, 22, 24, 0.7)",
          foreground: "#ffffff",
        }
      },
    },
  },
  plugins: [],
}
export default config