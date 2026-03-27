/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#161616',
          secondary: '#1f1f1f',
          hover: '#252525',
          border: '#333',
        }
      }
    },
  },
  plugins: [],
}
