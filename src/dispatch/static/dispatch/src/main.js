import { createApp } from "vue"
import App from "./App.vue"
import { vuetifyPlugin } from "./vuetify/"
import router from "./router/"
import store from "./store"
import { plugin, defaultConfig } from "@formkit/vue"
import { createProPlugin, autocomplete } from "@formkit/pro"

import "roboto-fontface/css/roboto/roboto-fontface.css"
import "font-awesome/css/font-awesome.css"
import "@formkit/themes/genesis"
import "./styles/index.scss"

import * as Sentry from "@sentry/vue"

const app = createApp(App)

// Configure sentry
let SENTRY_ENABLED = import.meta.env.VITE_DISPATCH_SENTRY_ENABLED
let SENTRY_DSN = import.meta.env.VITE_DISPATCH_SENTRY_DSN
let FORMKIT_ENTERPRISE_TOKEN = import.meta.env.FORMKIT_ENTERPRISE_TOKEN

let isUsingFormkitEnterprise = false

if (FORMKIT_ENTERPRISE_TOKEN) {
  const pro = createProPlugin(FORMKIT_ENTERPRISE_TOKEN, {
    autocomplete,
  })
  app.use(
    plugin,
    defaultConfig({
      plugins: [pro],
    })
  )
  isUsingFormkitEnterprise = true
} else {
  app.use(plugin, defaultConfig)
}

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
app.use(vuetifyPlugin)
app.use(router)
app.use(store)

app.mount("#app")

export { isUsingFormkitEnterprise }
