import Vue from "vue"
import Vuex from "vuex"
import { getField } from "vuex-map-fields"

import app from "@/app/store"
import auth from "@/auth/store"
import case_management from "@/case/store"
import case_priority from "@/case/priority/store"
import case_severity from "@/case/severity/store"
import case_type from "@/case/type/store"
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
import organization from "@/organization/store"
import plugin from "@/plugin/store"
import project from "@/project/store"
import query from "@/data/query/store"
import reference from "@/document/reference/store"
import runbook from "@/document/runbook/store"
import search from "@/search/store"
import service from "@/service/store"
import source from "@/data/source/store"
import sourceDataFormat from "@/data/source/dataFormat/store"
import sourceEnvironment from "@/data/source/environment/store"
import sourceStatus from "@/data/source/status/store"
import sourceTransport from "@/data/source/transport/store"
import sourceType from "@/data/source/type/store"
import signal from "@/signal/store"
import signalSuppressionRule from "@/signal/suppression_rule/store"
import signalDuplicationRule from "@/signal/duplication_rule/store"
import tag from "@/tag/store"
import tag_type from "@/tag_type/store"
import task from "@/task/store"
import team from "@/team/store"
import template from "@/document/template/store"
import term from "@/term/store"
import workflow from "@/workflow/store"

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    app,
    auth,
    case_management,
    case_priority,
    case_severity,
    case_type,
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
    organization,
    plugin,
    project,
    query,
    reference,
    route: {
      namespaced: true,
      getters: {
        getField,
      },
    },
    runbook,
    search,
    service,
    source,
    sourceDataFormat,
    sourceEnvironment,
    sourceStatus,
    sourceTransport,
    sourceType,
    signal,
    signalDuplicationRule,
    signalSuppressionRule,
    tag,
    tag_type,
    task,
    team,
    template,
    term,
    workflow,
  },
  strict: process.env.NODE_ENV !== "production",
})
