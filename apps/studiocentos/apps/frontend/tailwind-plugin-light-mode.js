/**
 * Tailwind Plugin per supportare la variante "light:"
 * Permette di usare light: come dark: ma invertito
 */
const plugin = require('tailwindcss/plugin');

module.exports = plugin(function({ addVariant }) {
  // Aggiunge la variante "light" che si attiva quando c'è la classe "light" su html
  addVariant('light', '.light &');
});
