import "@mdi/font/css/materialdesignicons.css" // Ensure you are using css-loader

import Vue from "vue"
import Vuetify from "vuetify"
import { TiptapVuetifyPlugin } from "tiptap-vuetify"
import "tiptap-vuetify/dist/main.css"

import { opts } from "./config"

Vue.use(Vuetify)

const vuetify = new Vuetify()

Vue.use(TiptapVuetifyPlugin, {
  // the next line is important! You need to provide the Vuetify Object to this place.
  vuetify, // same as "vuetify: vuetify"
  // optional, default to 'md' (default vuetify icons before v2.0.0)
  iconsGroup: "md",
})

export default new Vuetify(opts)
