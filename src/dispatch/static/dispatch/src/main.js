import Vue from "vue"
import App from "./App.vue"
import vuetify from "./vuetify/"
import router from "./router/"
import store from "./store"
import "./registerServiceWorker"
import "roboto-fontface/css/roboto/roboto-fontface.css"
import "font-awesome/css/font-awesome.css"

import * as Sentry from "@sentry/browser"
import * as Integrations from "@sentry/integrations"

//Sentry.init({
//  dsn: "https://6df40584b7814b2aab2f47d7b4a21124@sentry.mgmt.netflix.net/38",
//  integrations: [new Integrations.Vue({ Vue, attachProps: true })]
//})

Vue.config.productionTip = false

new Vue({
  vuetify,
  router,
  store,
  render: h => h(App)
}).$mount("#app")
