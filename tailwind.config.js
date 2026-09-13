/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  safelist: [
    "bg-[#EEF2FF]",
    "border-[#C7D2FE]",
    "bg-[#E0E7FF]",
    "text-[#7E22CE]",
    "bg-[#FAF5FF]",
    "border-[#E9D5FF]",
    "bg-[#F3E8FF]",
    "bg-[#ECFDF5]",
    "border-[#A7F3D0]",
    "text-[#047857]",
    "bg-[#D1FAE5]",
    "bg-[#F0F9FF]",
    "border-[#BAE6FD]",
    "text-[#0369A1]",
    "bg-[#E0F2FE]",
    "bg-[#FFFBEB]",
    "border-[#FDE68A]",
    "text-[#B45309]",
    "bg-[#FEF3C7]",
    "bg-[#FFF1F2]",
    "border-[#FECDD3]",
    "text-[#BE123C]",
    "bg-[#FFE4E6]",
    "border-l-[#7E22CE]",
    "border-l-[#047857]",
    "border-l-[#0369A1]",
    "border-l-[#B45309]",
    "border-l-[#BE123C]",
    "bg-[#f8f9ff]",
    "bg-[#1e293b]",
    "bg-[#0f172a]",
    "bg-[#334155]",
    "border-[#475569]",
    "bg-[#312e81]",
    "border-[#4338ca]",
    "bg-[#818CF8]",
    "py-0.2",
    "gap-4.5"
  ],
  theme: {
    extend: {
      colors: {
        surface: "rgb(var(--c-surface) / <alpha-value>)",
        "surface-container-lowest": "rgb(var(--c-surface-lowest) / <alpha-value>)",
        "surface-container-low": "rgb(var(--c-surface-low) / <alpha-value>)",
        "surface-container": "rgb(var(--c-surface-container) / <alpha-value>)",
        "surface-container-high": "rgb(var(--c-surface-high) / <alpha-value>)",
        "surface-container-highest": "rgb(var(--c-surface-highest) / <alpha-value>)",
        "on-surface": "rgb(var(--c-on-surface) / <alpha-value>)",
        "on-surface-variant": "rgb(var(--c-on-surface-variant) / <alpha-value>)",
        outline: "rgb(var(--c-outline) / <alpha-value>)",
        "outline-variant": "rgb(var(--c-outline-variant) / <alpha-value>)",
        primary: "rgb(var(--c-primary) / <alpha-value>)",
        "on-primary": "rgb(var(--c-on-primary) / <alpha-value>)",
        "primary-container": "rgb(var(--c-primary-container) / <alpha-value>)",
        "on-primary-container": "rgb(var(--c-on-primary-container) / <alpha-value>)",
        "primary-fixed": "rgb(var(--c-primary-fixed) / <alpha-value>)",
        "on-primary-fixed": "rgb(var(--c-on-primary-fixed) / <alpha-value>)",
        secondary: "rgb(var(--c-secondary) / <alpha-value>)",
        "on-secondary": "rgb(var(--c-on-secondary) / <alpha-value>)",
        "secondary-container": "rgb(var(--c-secondary-container) / <alpha-value>)",
        "on-secondary-container": "rgb(var(--c-on-secondary-container) / <alpha-value>)",
        "secondary-fixed": "rgb(var(--c-secondary-fixed) / <alpha-value>)",
        "on-secondary-fixed": "rgb(var(--c-on-secondary-fixed) / <alpha-value>)",
        tertiary: "rgb(var(--c-tertiary) / <alpha-value>)",
        "on-tertiary": "rgb(var(--c-on-tertiary) / <alpha-value>)",
        "tertiary-container": "rgb(var(--c-tertiary-container) / <alpha-value>)",
        "on-tertiary-container": "rgb(var(--c-on-tertiary-container) / <alpha-value>)",
        "tertiary-fixed": "rgb(var(--c-tertiary-fixed) / <alpha-value>)",
        "on-tertiary-fixed": "rgb(var(--c-on-tertiary-fixed) / <alpha-value>)",
        error: "rgb(var(--c-error) / <alpha-value>)",
        "on-error": "rgb(var(--c-on-error) / <alpha-value>)",
        "error-container": "rgb(var(--c-error-container) / <alpha-value>)",
        "on-error-container": "rgb(var(--c-on-error-container) / <alpha-value>)"
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      spacing: {
        xs: "0.25rem",
        sm: "0.5rem",
        md: "0.75rem",
        lg: "1rem",
        xl: "1.5rem",
        "0.2": "0.125rem",
        "4.5": "1.1rem"
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgba(15, 23, 42, 0.05)"
      }
    }
  },
  corePlugins: {
    preflight: true
  },
  plugins: [
    function () {
      return function raw({ addUtilities }) {
        addUtilities({
          ".text-headline-xl": { fontSize: "28px", lineHeight: "1.2", letterSpacing: "-0.5px" },
          ".text-headline-lg": { fontSize: "24px", lineHeight: "1.25", letterSpacing: "-0.3px" },
          ".text-headline-md": { fontSize: "20px", lineHeight: "1.3", letterSpacing: "-0.2px" },
          ".text-headline-sm": { fontSize: "18px", lineHeight: "1.35", letterSpacing: "-0.15px" },
          ".font-headline-xl": { fontFamily: "Plus Jakarta Sans", fontWeight: "700" },
          ".font-headline-lg": { fontFamily: "Plus Jakarta Sans", fontWeight: "700" },
          ".font-headline-md": { fontFamily: "Plus Jakarta Sans", fontWeight: "700" },
          ".font-headline-sm": { fontFamily: "Plus Jakarta Sans", fontWeight: "700" },
          ".text-body-lg": { fontSize: "16px", lineHeight: "1.55" },
          ".text-body-md": { fontSize: "14px", lineHeight: "1.5" },
          ".text-body-sm": { fontSize: "13px", lineHeight: "1.45" },
          ".font-body-lg": { fontFamily: "Plus Jakarta Sans", fontWeight: "500" },
          ".font-body-md": { fontFamily: "Plus Jakarta Sans", fontWeight: "500" },
          ".font-body-sm": { fontFamily: "Plus Jakarta Sans", fontWeight: "400" },
          ".text-label-lg": { fontSize: "14px", lineHeight: "1.3", letterSpacing: "0.1px" },
          ".text-label-md": { fontSize: "13px", lineHeight: "1.3", letterSpacing: "0.1px" },
          ".text-label-sm": { fontSize: "12px", lineHeight: "1.35", letterSpacing: "0.3px" },
          ".font-label-lg": { fontFamily: "Plus Jakarta Sans", fontWeight: "600" },
          ".font-label-md": { fontFamily: "Plus Jakarta Sans", fontWeight: "600" },
          ".font-label-sm": { fontFamily: "Plus Jakarta Sans", fontWeight: "500" }
        });
      };
    }
  ]
};