import "@mdi/font/css/materialdesignicons.css" // Ensure you are using css-loader

import Vue from "vue"
import Vuetify from "vuetify"

import { opts } from "./config"

Vue.use(Vuetify)

export default new Vuetify(opts)
