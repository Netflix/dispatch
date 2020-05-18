import Vue from "vue"
import Vuex from "vuex"

import app from "@/app/store"
import definition from "@/definition/store"
import incident from "@/incident/store"
import incident_type from "@/incident_type/store"
import incident_priority from "@/incident_priority/store"
import individual from "@/individual/store"
import policy from "@/policy/store"
import route from "@/route/store"
import search from "@/search/store"
import service from "@/service/store"
import team from "@/team/store"
import term from "@/term/store"
import auth from "@/auth/store"
import document from "@/document/store"
import tag from "@/tag/store"
import task from "@/task/store"
import plugin from "@/plugin/store"

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    app,
    auth,
    task,
    tag,
    definition,
    document,
    incident,
    incident_type,
    incident_priority,
    individual,
    policy,
    plugin,
    route,
    search,
    service,
    team,
    term
  },
  strict: process.env.NODE_ENV !== "production"
})
