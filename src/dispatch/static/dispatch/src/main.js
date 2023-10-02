import { createApp } from "vue"
import App from "./App.vue"
import { vuetifyPlugin } from "./vuetify/"
import router from "./router/"
import store from "./store"

import "roboto-fontface/css/roboto/roboto-fontface.css"
import "font-awesome/css/font-awesome.css"

import * as Sentry from "@sentry/vue"

const app = createApp(App)

// Configure sentry
let SENTRY_ENABLED = import.meta.env.VITE_DISPATCH_SENTRY_ENABLED
let SENTRY_DSN = import.meta.env.VITE_DISPATCH_SENTRY_DSN

if (SENTRY_ENABLED) {
  const APP_HOSTNAME = document.location.host

  let DSN = `https://1:1@${APP_HOSTNAME}/0`

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
