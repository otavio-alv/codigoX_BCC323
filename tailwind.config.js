/** tema da cartilha "primeiros passos no digital" do codigo x. */
/** @type {import('tailwindcss').config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        "codigo-fundo": "#F4F4F2",
        "codigo-texto": "#1E1E24",
        "codigo-agua": "#0F9A9E",
        "codigo-agua-escuro": "#0B7376",
        "codigo-coral": "#E2563F",
        "codigo-coral-escuro": "#C8402E",
        "codigo-amarelo": "#FFD84D",
        "codigo-amarelo-claro": "#FFF4C7",
      },
      fontFamily: {
        titulo: ['"Baloo 2"', "system-ui", "sans-serif"],
        texto: ["Poppins", "system-ui", "sans-serif"],
      },
      borderRadius: {
        cartilha: "14px",
        "cartilha-md": "20px",
        "cartilha-lg": "28px",
      },
      borderWidth: {
        3: "3px",
      },
      boxShadow: {
        solida: "4px 4px 0 #1E1E24",
        "solida-sm": "2px 2px 0 #1E1E24",
      },
      fontSize: {
        base: ["1rem", { lineHeight: "1.6" }],
      },
    },
  },
  plugins: [],
};
