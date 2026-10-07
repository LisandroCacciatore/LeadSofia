/** Tailwind del sitio de Sofía Strafile.
 *
 *  Los tokens están copiados VERBATIM del `tailwind.config` que el mockup definía en
 *  runtime para el CDN: son la fuente de verdad del diseño, no se re-derivan.
 *  Lo único que cambia es `backgroundImage['paper-texture']`: el mockup la traía de
 *  transparenttextures.com (un tercero) y el sitio no puede llamar a nadie en runtime,
 *  así que la textura pasa a ser un data-URI SVG local.
 */
module.exports = {
  darkMode: "class",
  content: ["./02-sitio/**/*.html"],
  theme: {
    extend: {
      colors: {
        primary: "#1F3A5F",
        accent: "#BC204B",
        "accent-hover": "#9A1A3E",
        "accent-dark": "#791431",
        "background-light": "#F7F5F2",
        "background-paper": "#E7DFD6",
        "background-dark": "#0e1a2b",
        "surface-dark": "#152840",
        slate: {
          50: "#f9fafb",
          100: "#f3f4f6",
          200: "#e6e8eb",
          300: "#d1d5db",
          400: "#a8adb5",
          500: "#8A8F96",
          600: "#6e7278",
          700: "#53565a",
          800: "#37393c",
          900: "#1c1d1e",
        },
      },
      fontFamily: {
        display: ["Playfair Display", "serif"],
        sans: ["Inter", "sans-serif"],
      },
      backgroundImage: {
        "paper-texture":
          "repeating-linear-gradient(135deg, rgba(31,58,95,0.022) 0 2px, transparent 2px 6px)",
      },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};
