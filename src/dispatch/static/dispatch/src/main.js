import { createApp } from "vue"
import App from "./App.vue"
import { vuetifyPlugin } from "./vuetify/"
import router from "./router/"
import store from "./store"
import "@formkit/themes/genesis"
import "@formkit/pro/genesis"

import { createProPlugin, inputs } from "@formkit/pro"
import { plugin, defaultConfig } from "@formkit/vue"
import VResizeDrawer from "vuetify3-resize-drawer"

import "roboto-fontface/css/roboto/roboto-fontface.css"
import "font-awesome/css/font-awesome.css"
import "./styles/index.scss"

import * as Sentry from "@sentry/vue"

const app = createApp(App)

// Configure sentry
let SENTRY_ENABLED = import.meta.env.VITE_DISPATCH_SENTRY_ENABLED
let SENTRY_DSN = import.meta.env.VITE_DISPATCH_SENTRY_DSN
const FORMKIT_PRO_PROJECT_KEY = import.meta.env.VITE_FORMKIT_PRO_PROJECT_KEY


if (SENTRY_ENABLED) {
  const APP_HOSTNAME = document.location.host

  let DSN = `https://1:1@${APP_HOSTNAME}/api/0`

  // Allow global override
  if (SENTRY_DSN) {
    DSN = SENTRY_DSN
  }
  Sentry.init({
    app,
    dsn: DSN,
  })
}

// Configure plugins
if (FORMKIT_PRO_PROJECT_KEY) {
  const pro = createProPlugin(FORMKIT_PRO_PROJECT_KEY, inputs)
  app.use(plugin, defaultConfig({ plugins: [pro] }))
} else {
  app.use(plugin, defaultConfig)
}
app.use(vuetifyPlugin)
app.use(router)
app.use(store)
app.component("VResizeDrawer", VResizeDrawer)

app.mount("#app")
