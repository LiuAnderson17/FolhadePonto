/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",          // todos os seus templates Django
    "./ponto/templates/**/*.html",    // se criar subpastas no app
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}