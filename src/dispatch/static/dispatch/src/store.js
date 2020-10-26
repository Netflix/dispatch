import Vue from "vue"
import Vuex from "vuex"

import app from "@/app/store"
import auth from "@/auth/store"
import definition from "@/definition/store"
import document from "@/document/store"
import feedback from "@/feedback/store"
import incident from "@/incident/store"
import incident_priority from "@/incident_priority/store"
import incident_type from "@/incident_type/store"
import individual from "@/individual/store"
import plugin from "@/plugin/store"
import policy from "@/policy/store"
import route from "@/route/store"
import search from "@/search/store"
import service from "@/service/store"
import tag from "@/tag/store"
import tag_type from "@/tag_type/store"
import task from "@/task/store"
import team from "@/team/store"
import term from "@/term/store"
import workflow from "@/workflow/store"

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    app,
    auth,
    definition,
    document,
    feedback,
    incident,
    incident_priority,
    incident_type,
    individual,
    plugin,
    policy,
    route,
    search,
    service,
    tag,
    tag_type,
    task,
    team,
    term,
    workflow
  },
  strict: process.env.NODE_ENV !== "production"
})
