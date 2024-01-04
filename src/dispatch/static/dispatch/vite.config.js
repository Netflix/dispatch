import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import vuetify from "vite-plugin-vuetify"
import monacoEditorPlugin from "vite-plugin-monaco-editor"
import topLevelAwait from "vite-plugin-top-level-await"

import Components from "unplugin-vue-components/vite"

import path from "path"

export default defineConfig({
  plugins: [
    vue(),
    vuetify(),
    monacoEditorPlugin({ languageWorkers: ["json"] }),
    Components(),
    {
      resolveId(id) {
        if (id.includes("vee-validate")) {
          return "virtual:vee-validate"
        }
      },
      load(id) {
        if (id.includes("vee-validate")) {
          return `
          let ValidationObserver, ValidationProvider, extend, localize, setInteractionMode, configure, mapFields, ErrorMessage, required, email;
          extend = localize = setInteractionMode = configure = mapFields = required = email = () => {}
          ValidationObserver = ValidationProvider = (_, { slots }) => slots.default({ errors: [], messages: [] })
          export { ValidationObserver, ValidationProvider, extend, localize, setInteractionMode, configure, mapFields, ErrorMessage, required, email };`
        }
      },
    },
    topLevelAwait({
      // The export name of top-level await promise for each chunk module
      promiseExportName: "__tla",
      // The function to generate import names of top-level await promise in each chunk module
      promiseImportName: (i) => `__tla_${i}`,
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
