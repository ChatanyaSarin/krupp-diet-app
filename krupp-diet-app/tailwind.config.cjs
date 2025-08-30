/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./app/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    // keep brand utilities if used via template strings
    "bg-uc-blue","hover:bg-uc-blue/90",
    "bg-uc-gold","hover:bg-uc-gold/90",
    "text-uc-blue","text-uc-gold","border-uc-blue","border-uc-gold",
  ],
  theme: {
    extend: {
      colors: {
        "uc-blue": "#182B49",
        "uc-gold": "#C69214",
      },
      boxShadow: {
        soft: "0 8px 30px rgba(0,0,0,0.08)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
