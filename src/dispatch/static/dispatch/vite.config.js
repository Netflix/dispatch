import { defineConfig } from "vite"
import vue2 from "@vitejs/plugin-vue2"
import monacoEditorPlugin from "vite-plugin-monaco-editor"
import { VuetifyResolver } from "unplugin-vue-components/resolvers"
import { VitePWA } from "vite-plugin-pwa"

import Components from "unplugin-vue-components/vite"

import path from "path"

export default defineConfig({
  plugins: [
    vue2(),
    VitePWA(),
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
        target: "http://localhost:8000",
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
