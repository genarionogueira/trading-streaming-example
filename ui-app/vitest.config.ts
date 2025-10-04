import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
  },
  css: {
    // Avoid loading PostCSS/Tailwind in tests
    postcss: undefined,
  },
});
