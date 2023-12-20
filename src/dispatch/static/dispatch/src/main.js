import { createApp } from "vue"
import App from "./App.vue"
import { vuetifyPlugin } from "./vuetify/"
import router from "./router/"
import store from "./store"
import { plugin, defaultConfig } from "@formkit/vue"

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

if (FORMKIT_ENTERPRISE_TOKEN) {
  import("@formkit-enterprise/pro").then((module) => {
    // Use the module here
  })
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
app.use(plugin, defaultConfig)
app.use(vuetifyPlugin)
app.use(router)
app.use(store)

app.mount("#app")
