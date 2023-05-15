import { defineConfig } from "vite"
import vue2 from "@vitejs/plugin-vue2"
import monacoEditorPlugin from "vite-plugin-monaco-editor"
import { VuetifyResolver } from "unplugin-vue-components/resolvers"

import Components from "unplugin-vue-components/vite"

import path from "path"

export default defineConfig({
  plugins: [
    vue2(),
    monacoEditorPlugin({ languageWorkers: ["json"] }),
    Components({
      resolvers: [
        // Vuetify
        VuetifyResolver(),
      ],
    }),
  ],
  server: {
    port: 8080,
    proxy: {
      "^/api": {
        target: "http://127.0.0.1:8000",
        ws: false,
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: [
      {
        find: "@",
        replacement: path.resolve(__dirname, "./src"),
      },
    ],
  },
  build: {
    chunkSizeWarningLimit: 600,
  },
})
