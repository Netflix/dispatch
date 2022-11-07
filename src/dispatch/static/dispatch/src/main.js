import Vue from "vue"
import App from "./App.vue"
import vuetify from "./vuetify/"
import router from "./router/"
import store from "./store"
import axios from "axios"

import "./filters.js"
import "roboto-fontface/css/roboto/roboto-fontface.css"
import "font-awesome/css/font-awesome.css"
import { sync } from "vuex-router-sync"

import * as Sentry from "@sentry/browser"
import * as Integrations from "@sentry/integrations"

import VueClipboard from "vue-clipboard2"
import VueMarkdown from "vue-markdown"

// initialize the app settings before mounting the app
function initialize() {
  return axios.get("/api/v1/settings").then((response) => {
    for (const [key, value] of Object.entries(response.data)) {
      localStorage.setItem(key, value)
    }
  })
}

initialize().then(() => {
  // Configure sentry
  let SENTRY_ENABLED = localStorage.getItem("SENTRY_ENABLED")
  let SENTRY_DSN = localStorage.getItem("SENTRY_DSN")
  if (SENTRY_ENABLED) {
    const APP_HOSTNAME = document.location.host

    let DSN = `https://1:1@${APP_HOSTNAME}/0`

    // Allow global override
    if (SENTRY_DSN) {
      DSN = SENTRY_DSN
    }
    Sentry.init({
      dsn: DSN,
      integrations: [new Integrations.Vue({ Vue, attachProps: true })],
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
})
