import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    server: {
      deps: {
        inline: ["vuetify"],
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"), // provide an absolute path to your src directory
    },
  },
})
