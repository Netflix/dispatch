import Vue from "vue"
import Vuex from "vuex"
import { getField } from "vuex-map-fields"

import app from "@/app/store"
import auth from "@/auth/store"
import definition from "@/definition/store"
import document from "@/document/store"
import feedback from "@/feedback/store"
import incident from "@/incident/store"
import incident_cost_type from "@/incident_cost_type/store"
import incident_priority from "@/incident_priority/store"
import incident_type from "@/incident_type/store"
import individual from "@/individual/store"
import notification from "@/notification/store"
import notification_backend from "@/app/notificationStore"
import plugin from "@/plugin/store"
import search from "@/search/store"
import service from "@/service/store"
import tag from "@/tag/store"
import tag_type from "@/tag_type/store"
import task from "@/task/store"
import team from "@/team/store"
import term from "@/term/store"
import project from "@/project/store"
import organization from "@/organization/store"
import workflow from "@/workflow/store"
import template from "@/document/template/store"
import runbook from "@/document/runbook/store"
import reference from "@/document/reference/store"
import source from "@/data/source/store"
import sourceEnvironment from "@/data/source/environment/store"
import sourceDataFormat from "@/data/source/dataFormat/store"
import sourceStatus from "@/data/source/status/store"
import sourceTransport from "@/data/source/transport/store"
import sourceType from "@/data/source/type/store"
import query from "@/data/query/store"

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    app,
    auth,
    definition,
    document,
    feedback,
    incident,
    incident_cost_type,
    incident_priority,
    incident_type,
    individual,
    notification,
    notification_backend,
    plugin,
    project,
    organization,
    search,
    service,
    tag,
    tag_type,
    task,
    template,
    team,
    term,
    workflow,
    runbook,
    reference,
    source,
    sourceEnvironment,
    sourceDataFormat,
    sourceStatus,
    sourceTransport,
    sourceType,
    query,
    route: {
      namespaced: true,
      getters: {
        getField,
      },
    },
  },
  strict: process.env.NODE_ENV !== "production",
})
