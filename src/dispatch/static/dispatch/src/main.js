import Vue from "vue"
import App from "./App.vue"
import vuetify from "./vuetify/"
import router from "./router/"
import store from "./store"
import filters from "./filters" // eslint-disable-line no-unused-vars
import "./registerServiceWorker"
import "roboto-fontface/css/roboto/roboto-fontface.css"
import "font-awesome/css/font-awesome.css"
import { sync } from "vuex-router-sync"

import * as Sentry from "@sentry/browser"
import * as Integrations from "@sentry/integrations"

import VueClipboard from "vue-clipboard2"

// Configure sentry
if (process.env.VUE_APP_SENTRY_ENABLED) {
  const APP_HOSTNAME = document.location.host

  let DSN = `https://1:1@${APP_HOSTNAME}/0`

  // Allow global override
  if (process.env.VUE_APP_SENTRY_DSN) {
    DSN = process.env.VUE_APP_SENTRY_DSN
  }

  Sentry.init({
    dsn: DSN,
    integrations: [new Integrations.Vue({ Vue, attachProps: true })],
  })
  Sentry.setTag(process.env.VUE_APP_SENTRY_APP_KEY, APP_HOSTNAME)
}

console.log(Sentry.config)
console.log(process.env)
// Send the Hello Radar! message (if it wasn't sent yet)
if (!"_sentry_hello_" in localStorage) {
  Sentry.captureMessage("Hello Sentry!", "warning")
  localStorage["_sentry_hello_"] = true
}

sync(store, router, { moduleName: "route" })

Vue.config.productionTip = false

Vue.use(VueClipboard)

new Vue({
  vuetify,
  router,
  store,
  render: (h) => h(App),
}).$mount("#app")
