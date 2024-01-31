import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

import tailwind from "tailwindcss";
import autoprefixer from "autoprefixer";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  css: {
    postcss: {
      plugins: [tailwind(), autoprefixer()],
    },
  },
  build: {
        sourcemap: true,
    },
  resolve: {
    alias: {
      'vue': 'vue/dist/vue.esm-bundler.js',
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
