const isVitest = process.env.VITEST === "true";

const config = {
  plugins: isVitest ? [] : ["@tailwindcss/postcss"],
};

export default config;
