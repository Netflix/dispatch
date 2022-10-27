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
import VueMarkdown from "vue-markdown"

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
  process.env.VUE_APP_SENTRY_TAGS.split(",").forEach(function (item) {
    var parts = item.split(":")
    Sentry.setTag(parts[0], parts[1])
  })
}

sync(store, router, { moduleName: "route" })

Vue.config.productionTip = false

Vue.use(VueClipboard)
Vue.use(VueMarkdown)

new Vue({
  vuetify,
  router,
  store,
  render: (h) => h(App),
}).$mount("#app")
