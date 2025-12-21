module.exports = {
  darkMode: false,
  plugins: {
    "@tailwindcss/postcss": {},
    "postcss-simple-vars": {},
    "postcss-nested": {},
  },
  daisyui: {
    themes: ["light", "dark"], // Or true/false depending on version
    darkTheme: "light",
  },
};
