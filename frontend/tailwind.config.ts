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
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "#ecad29", // ring to Gold
        background: "#0a0a0b", // background
        foreground: "#ffffff",
        primary: {
          DEFAULT: "#ecad29", // Change Blue to Gold
          foreground: "#000000",
        },
        secondary: {
          DEFAULT: "#161618",
          foreground: "#ffffff",
        },
      },
      // ... rest of config
    },
  },
  plugins: [],
}
export default config