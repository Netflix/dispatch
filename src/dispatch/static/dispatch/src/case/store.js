import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import CaseApi from "@/case/api"
import ProjectApi from "@/project/api"
import PluginApi from "@/plugin/api"
import AuthApi from "@/auth/api"
import router from "@/router"

const resolutionTooltips = {
  Benign:
    "The event was legitimate but posed no security threat, such as expected behavior from a known application or user.",
  Contained:
    "(True positive) The event was a legitimate threat but was contained to prevent further spread or damage.",
  Escalated: "There was enough information to create an incident based on the security event.",
  "False Positive": "The event was incorrectly flagged as a security event.",
  "Information Gathered":
    "Used when a case was opened with the primary purpose of collecting information.",
  "Insufficient Information":
    "There was not enough information to determine the nature of the event conclusively.",
  Mitigated:
    "(True Positive) The event was a legitimate security threat and was successfully mitigated before causing harm.",
  "Operational Error":
    "The event was caused by a mistake in system configuration or user operation, not malicious activity.",
  "Policy Violation":
    "The event was a breach of internal security policies but did not result in a security incident.",
  "User Acknowledged":
    "While the event was suspicious it was confirmed by the actor to be intentional.",
}

const resolutionReasons = Object.keys(resolutionTooltips)

const getDefaultSelectedState = () => {
  return {
    assignee: null,
    case_costs: [],
    case_priority: null,
    case_severity: null,
    case_type: null,
    closed_at: null,
    conversation: null,
    dedicated_channel: true,
    description: null,
    documents: [],
    duplicates: [],
    escalated_at: null,
    events: [],
    genai_analysis: null,
    groups: [],
    id: null,
    incidents: [],
    loading: false,
    name: null,
    participant: null,
    project: null,
    related: [],
    reported_at: null,
    reporter: null,
    resolution: null,
    resolution_reason: null,
    saving: false,
    signals: [],
    status: null,
    storage: null,
    tags: [],
    ticket: null,
    title: null,
    triage_at: null,
    updated_at: null,
    visibility: null,
    workflow_instances: null,
    event: false,
    currentEvent: {
      uuid: null,
      source: "",
      description: "",
      started_at: null,
      ended_at: null,
      type: "Custom event",
      details: {},
      owner: "",
      pinned: false,
    },
  }
}

const getDefaultReportState = () => {
  return {}
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showDeleteDialog: false,
    showEditSheet: false,
    showEscalateDialog: false,
    showExport: false,
    showHandoffDialog: false,
    showClosedDialog: false,
    showNewSheet: false,
    showEditEventDialog: false,
    showDeleteEventDialog: false,
  },
  report: {
    ...getDefaultReportState(),
  },
  table: {
    rows: {
      items: [],
      total: null,
      selected: [],
    },
    options: {
      filters: {
        assignee: [],
        case_priority: [],
        case_severity: [],
        case_type: [],
        project: [],
        status: [],
        tag: [],
        tag_type: [],
        reported_at: {
          start: null,
          end: null,
        },
        closed_at: {
          start: null,
          end: null,
        },
        participant: null,
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["reported_at"],
      descending: [true],
    },
    saving: false,
    loading: false,
    bulkEditLoading: false,
  },
  timeline_filters: {
    field_updates: true,
    assessment_updates: false,
    user_curated_events: false,
    participant_updates: true,
    other_events: true,
  },
  default_project: null,
  current_user_role: null,
  resolutionReasons,
  resolutionTooltips,
}

const getters = {
  getField,
  tableOptions({ state }) {
    // format our filters
    return state.table.options
  },
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let default_params = {
      filter: { field: "default", op: "==", value: true },
    }
    ProjectApi.getAll(default_params).then((response) => {
      commit("SET_DEFAULT_PROJECT", response.data.items[0])
    })
    AuthApi.getUserRole().then((response) => {
      commit("SET_CURRENT_USER_ROLE", response.data)
    })
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Case")
    return CaseApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  get({ commit, state }) {
    return CaseApi.get(state.selected.id).then((response) => {
      commit("SET_SELECTED", response.data)
    })
  },
  getDetails({ commit, state }, payload) {
    commit("SET_SELECTED_LOADING", true)
    if ("id" in payload) {
      return CaseApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
      })
    } else if ("name" in payload) {
      // this is kinda dirty
      return CaseApi.getAll({
        filter: JSON.stringify([
          { and: [{ model: "Case", field: "name", op: "==", value: payload.name }] },
        ]),
      }).then((response) => {
        if (response.data.items.length) {
          // get the full data set
          return CaseApi.get(response.data.items[0].id).then((response) => {
            commit("SET_SELECTED", response.data)
            commit("SET_SELECTED_LOADING", false)
          })
        } else {
          commit(
            "notification_backend/addBeNotification",
            {
              text: `Case '${payload.name}' could not be found.`,
              type: "exception",
            },
            { root: true }
          )
          commit("SET_DIALOG_SHOW_EDIT_SHEET", false)
        }
        commit("SET_SELECTED_LOADING", false)
      })
    }
  },
  showNewSheet({ commit }, value) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", true)
    if (value) {
      commit("SET_SELECTED", value)
    }
  },
  closeNewSheet({ commit }) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", false)
    commit("RESET_SELECTED")
  },
  showEditSheet({ commit }) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", true)
  },
  closeEditSheet({ commit }) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", false)
    commit("RESET_SELECTED")
    router.push({ name: "CaseTable" })
  },
  showDeleteDialog({ commit }, value) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", value)
  },
  closeDeleteDialog({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  showEscalateDialog({ commit }, value) {
    commit("SET_DIALOG_ESCALATE", true)
    commit("SET_SELECTED", value)
  },
  closeEscalateDialog({ commit }) {
    commit("SET_DIALOG_ESCALATE", false)
    commit("RESET_SELECTED")
    commit("incident/RESET_SELECTED", null, { root: true })
    // force page reload to pick up the change to status
    window.location.reload()
  },
  showHandoffDialog({ commit }, value) {
    commit("SET_DIALOG_SHOW_HANDOFF", true)
    commit("SET_SELECTED", value)
  },
  closeHandoffDialog({ commit }) {
    commit("SET_DIALOG_SHOW_HANDOFF", false)
    commit("RESET_SELECTED")
  },
  showClosedDialog({ commit }, value) {
    commit("SET_DIALOG_SHOW_CLOSED", true)
    commit("SET_SELECTED", value)
  },
  closeClosedDialog({ commit }) {
    commit("SET_DIALOG_SHOW_CLOSED", false)
    commit("RESET_SELECTED")
  },
  showExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", true)
  },
  closeExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", false)
  },
  escalate({ commit, dispatch }, payload) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.escalate(state.selected.id, payload).then((response) => {
      commit("incident/SET_SELECTED", response.data, { root: true })
      commit("SET_SELECTED_LOADING", false)

      return new Promise((resolve) => {
        const interval = setInterval(() => {
          dispatch("incident/get", response.data.id, { root: true }).then((incidentData) => {
            if (incidentData.conversation && incidentData.storage && incidentData.documents) {
              clearInterval(interval)
              resolve(incidentData)
            }
          })
        }, 5000)
      })
    })
  },
  report({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.create(state.selected)
      .then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
        var interval = setInterval(function () {
          if (state.selected.id) {
            dispatch("get")
          }

          // TODO this is fragile but we don't set anything as "created"
          if (state.selected.conversation) {
            clearInterval(interval)
          }
        }, 5000)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  createAllResources({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.createAllResources(state.selected.id)
      .then(() => {
        CaseApi.get(state.selected.id).then((response) => {
          commit("SET_SELECTED", response.data)
          dispatch("getEnabledPlugins").then((enabledPlugins) => {
            // Poll the server for resource creation updates.
            var interval = setInterval(function () {
              if (
                state.selected.conversation ^ enabledPlugins.includes("conversation") ||
                state.selected.documents ^ enabledPlugins.includes("document") ||
                state.selected.storage ^ enabledPlugins.includes("storage") ||
                state.selected.groups ^ enabledPlugins.includes("participant-group") ||
                state.selected.ticket ^ enabledPlugins.includes("ticket")
              ) {
                dispatch("get").then(() => {
                  clearInterval(interval)
                  commit("SET_SELECTED_LOADING", false)
                  commit(
                    "notification_backend/addBeNotification",
                    { text: "Resources(s) created successfully.", type: "success" },
                    { root: true }
                  )
                })
              }
            }, 5000)
          })
        })
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  createCaseChannel({ commit, dispatch }) {
    state.selected.dedicated_channel = true
    return CaseApi.createCaseChannel(state.selected.id)
      .then(() => {
        CaseApi.get(state.selected.id).then((response) => {
          commit("SET_SELECTED", response.data)
          dispatch("getEnabledPlugins").then((enabledPlugins) => {
            // Poll the server for resource creation updates.
            var interval = setInterval(function () {
              if (
                state.selected.conversation ^
                enabledPlugins.includes("conversation") ^
                !state.selected.conversation.thread_id
              ) {
                dispatch("get").then(() => {
                  clearInterval(interval)
                  commit("SET_SELECTED_LOADING", false)
                  commit(
                    "notification_backend/addBeNotification",
                    { text: "Conversation channel created successfully.", type: "success" },
                    { root: true }
                  )
                })
              }
            }, 5000)
          })
        })
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  save({ commit, dispatch }) {
    if (Array.isArray(state.selected.reporter)) {
      state.selected.reporter = state.selected.reporter[0]
    }
    if (Array.isArray(state.selected.assignee)) {
      state.selected.assignee = state.selected.assignee[0]
    }
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return CaseApi.create(state.selected)
        .then(() => {
          dispatch("closeNewSheet")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Case created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return CaseApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeEditSheet")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Case updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  saveBulk({ commit, dispatch }, payload) {
    commit("SET_BULK_EDIT_LOADING", true)
    return CaseApi.bulkUpdate(state.table.rows.selected, payload)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Case(s) updated successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(() => {
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  deleteBulk({ commit, dispatch }) {
    commit("SET_BULK_EDIT_LOADING", true)
    return CaseApi.bulkDelete(state.table.rows.selected)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Case(s) deleted successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(() => {
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  deleteCase({ commit, dispatch }) {
    return CaseApi.delete(state.selected.id).then(function () {
      dispatch("closeDeleteDialog")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Case deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
  resetSelected({ commit }) {
    commit("RESET_SELECTED")
  },
  joinCase({ commit }, caseId) {
    CaseApi.join(caseId, {}).then(() => {
      commit(
        "notification_backend/addBeNotification",
        { text: "You have successfully joined the case.", type: "success" },
        { root: true }
      )
    })
  },
  getEnabledPlugins() {
    if (!state.selected.project) {
      return false
    }
    return PluginApi.getAllInstances({
      filter: JSON.stringify({
        and: [
          {
            model: "PluginInstance",
            field: "enabled",
            op: "==",
            value: "true",
          },
          {
            model: "Project",
            field: "name",
            op: "==",
            value: state.selected.project.name,
          },
        ],
      }),
      itemsPerPage: 50,
    }).then((response) => {
      return response.data.items.reduce((result, item) => {
        if (item.plugin) {
          result.push(item.plugin.type)
        }
        return result
      }, [])
    })
  },
  // Timeline event actions
  showNewEventDialog({ commit }, started_at) {
    commit("SET_SELECTED_CURRENT_EVENT", {
      uuid: null,
      source: "Case Participant",
      description: "",
      started_at: started_at,
      ended_at: started_at,
      type: "Custom event",
      details: {},
      owner: "",
      pinned: false,
    })
    commit("SET_DIALOG_EDIT_EVENT", true)
  },
  showNewEditEventDialog({ commit }, event) {
    commit("SET_SELECTED_CURRENT_EVENT", {
      uuid: event.uuid,
      source: event.source,
      description: event.description,
      started_at: event.started_at,
      ended_at: event.started_at,
      type: event.type,
      details: event.details,
      owner: event.owner,
      pinned: event.pinned,
    })
    commit("SET_DIALOG_EDIT_EVENT", true)
  },
  showDeleteEventDialog({ commit }, event) {
    commit("SET_SELECTED_CURRENT_EVENT", {
      started_at: event.started_at,
      description: event.description,
      uuid: event.uuid,
    })
    commit("SET_DIALOG_DELETE_EVENT", true)
  },
  showNewPreEventDialog({ commit }, started_at) {
    commit("SET_SELECTED_CURRENT_EVENT", {
      uuid: null,
      source: "Case Participant",
      description: "",
      started_at: started_at,
      ended_at: started_at,
      type: "Custom event",
      details: {},
      owner: "",
      pinned: false,
    })
    commit("SET_DIALOG_EDIT_EVENT", true)
  },
  closeEditEventDialog({ commit }) {
    commit("SET_DIALOG_EDIT_EVENT", false)
  },
  closeDeleteEventDialog({ commit }) {
    commit("SET_DIALOG_DELETE_EVENT", false)
  },
  storeNewEvent({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.createNewEvent(state.selected.id, {
      source: "Case Participant",
      description: state.selected.currentEvent.description,
      started_at: state.selected.currentEvent.started_at,
      type: "Custom event",
      details: {},
    })
      .then(() => {
        dispatch("getDetails", { id: state.selected.id })
        commit("SET_DIALOG_EDIT_EVENT", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Event created successfully.", type: "success" },
          { root: true }
        )
        commit("SET_SELECTED_LOADING", false)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  updateExistingEvent({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.updateEvent(state.selected.id, {
      uuid: state.selected.currentEvent.uuid,
      source: state.selected.currentEvent.source,
      description: state.selected.currentEvent.description,
      started_at: state.selected.currentEvent.started_at,
      ended_at: state.selected.currentEvent.ended_at,
      type: state.selected.currentEvent.type || "Custom event",
      details: state.selected.currentEvent.details || {},
      owner: state.selected.currentEvent.owner || "",
      pinned: state.selected.currentEvent.pinned || false,
    })
      .then(() => {
        dispatch("getDetails", { id: state.selected.id })
        commit("SET_DIALOG_EDIT_EVENT", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Event updated successfully.", type: "success" },
          { root: true }
        )
        commit("SET_SELECTED_LOADING", false)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  deleteEvent({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.deleteEvent(state.selected.id, state.selected.currentEvent.uuid)
      .then(() => {
        dispatch("getDetails", { id: state.selected.id })
        commit("SET_DIALOG_DELETE_EVENT", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Event deleted successfully.", type: "success" },
          { root: true }
        )
        commit("SET_SELECTED_LOADING", false)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  togglePin({ commit, dispatch }, event) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.updateEvent(state.selected.id, {
      uuid: event.uuid,
      source: event.source,
      description: event.description,
      started_at: event.started_at,
      ended_at: event.started_at,
      type: event.type || "Custom event",
      details: event.details || {},
      owner: event.owner || "",
      pinned: !event.pinned,
    })
      .then(() => {
        dispatch("getDetails", { id: state.selected.id })
        commit("SET_SELECTED_LOADING", false)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  exportDoc({ commit }, timeline_filters) {
    commit(
      "notification_backend/addBeNotification",
      { text: "Timeline export initiated. This may take a few minutes.", type: "success" },
      { root: true }
    ),
      CaseApi.exportTimeline(state.selected.id, timeline_filters)
        .then(() => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Timeline exported successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_DIALOG_EDIT_EVENT", false)
        })
  },
}

const mutations = {
  updateField,
  addCaseCost(state, value) {
    state.selected.case_costs.push(value)
  },
  removeCaseCost(state, idx) {
    state.selected.case_costs.splice(idx, 1)
  },
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    // reset selected on table load
    value["selected"] = []
    state.table.rows = value
  },
  SET_DIALOG_SHOW_EDIT_SHEET(state, value) {
    state.dialogs.showEditSheet = value
  },
  SET_DIALOG_SHOW_NEW_SHEET(state, value) {
    state.dialogs.showNewSheet = value
  },
  SET_DIALOG_SHOW_EXPORT(state, value) {
    state.dialogs.showExport = value
  },
  SET_DIALOG_SHOW_HANDOFF(state, value) {
    state.dialogs.showHandoffDialog = value
  },
  SET_DIALOG_SHOW_CLOSED(state, value) {
    state.dialogs.showClosedDialog = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showDeleteDialog = value
  },
  SET_DIALOG_ESCALATE(state, value) {
    state.dialogs.showEscalateDialog = value
  },
  SET_FILTERS(state, payload) {
    state.table.options.filters = payload
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_BULK_EDIT_LOADING(state, value) {
    state.table.bulkEditLoading = value
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  },
  SET_SELECTED_SAVING(state, value) {
    state.selected.saving = value
  },
  SET_DEFAULT_PROJECT(state, value) {
    state.default_project = value
  },
  SET_CURRENT_USER_ROLE(state, value) {
    state.current_user_role = value
  },
  SET_SELECTED_CURRENT_EVENT(state, value) {
    state.selected.currentEvent = value
  },
  SET_DIALOG_EDIT_EVENT(state, value) {
    state.dialogs.showEditEventDialog = value
  },
  SET_DIALOG_DELETE_EVENT(state, value) {
    state.dialogs.showDeleteEventDialog = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
