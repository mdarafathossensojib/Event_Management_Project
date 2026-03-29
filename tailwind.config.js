/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./**/templates/**/**/*.html",
    "./**/*.py",  
    "./**/*.js",  
  ],
  theme: {
    extend: {
        colors: {
        primary: "#22d3ee",
        background: "#000000",
        card: "#18181b",
      }
    },
  },
  plugins: [],
}

