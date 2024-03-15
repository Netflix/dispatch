import { createStore } from "vuex"

import app from "@/app/store"
import auth from "@/auth/store"
import case_management from "@/case/store"
import case_priority from "@/case/priority/store"
import case_severity from "@/case/severity/store"
import case_type from "@/case/type/store"
import cost_model from "@/cost_model/store"
import definition from "@/definition/store"
import document from "@/document/store"
import email_templates from "@/email_templates/store"
import entity from "@/entity/store"
import entity_type from "@/entity_type/store"
import forms from "@/forms/store"
import forms_table from "@/forms/table/store"
import forms_type from "@/forms/types/store"
import incident_feedback from "@/feedback/incident/store"
import incident from "@/incident/store"
import incident_cost_type from "@/incident_cost_type/store"
import incident_priority from "@/incident/priority/store"
import incident_severity from "@/incident/severity/store"
import incident_type from "@/incident/type/store"
import individual from "@/individual/store"
import notification from "@/notification/store"
import notification_backend from "@/app/notificationStore"
import organization from "@/organization/store"
import playground from "@/entity_type/playground/store"
import plugin from "@/plugin/store"
import project from "@/project/store"
import query from "@/data/query/store"
import reference from "@/document/reference/store"
import runbook from "@/document/runbook/store"
import search from "@/search/store"
import service from "@/service/store"
import service_feedback from "@/feedback/service/store"
import signal from "@/signal/store"
import signalEngagement from "@/signal/engagement/store"
import signalFilter from "@/signal/filter/store"
import source from "@/data/source/store"
import sourceDataFormat from "@/data/source/dataFormat/store"
import sourceEnvironment from "@/data/source/environment/store"
import sourceStatus from "@/data/source/status/store"
import sourceTransport from "@/data/source/transport/store"
import sourceType from "@/data/source/type/store"
import tag from "@/tag/store"
import tag_type from "@/tag_type/store"
import task from "@/task/store"
import team from "@/team/store"
import template from "@/document/template/store"
import term from "@/term/store"
import workflow from "@/workflow/store"

export default createStore({
  modules: {
    app,
    auth,
    case_management,
    case_priority,
    case_severity,
    case_type,
    definition,
    document,
    email_templates,
    entity,
    entity_type,
    forms,
    forms_table,
    forms_type,
    incident_feedback,
    incident,
    cost_model,
    incident_cost_type,
    incident_priority,
    incident_severity,
    incident_type,
    individual,
    notification,
    notification_backend,
    organization,
    playground,
    plugin,
    project,
    query,
    reference,
    runbook,
    search,
    service,
    service_feedback,
    source,
    sourceDataFormat,
    sourceEnvironment,
    sourceStatus,
    sourceTransport,
    sourceType,
    signal,
    signalEngagement,
    signalFilter,
    tag,
    tag_type,
    task,
    team,
    template,
    term,
    workflow,
  },
})
