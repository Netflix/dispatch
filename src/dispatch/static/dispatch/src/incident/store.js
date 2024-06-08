import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentApi from "@/incident/api"
import ProjectApi from "@/project/api"
import PluginApi from "@/plugin/api"
import AuthApi from "@/auth/api"
import router from "@/router"
import moment from "moment-timezone"

const getDefaultSelectedState = () => {
  return {
    cases: [],
    commander: null,
    conference: null,
    conversation: null,
    created_at: null,
    description: null,
    documents: null,
    duplicates: [],
    events: null,
    id: null,
    incident_costs: null,
    incident_priority: null,
    incident_severity: null,
    incident_type: null,
    name: null,
    participant: null,
    project: null,
    reported_at: null,
    reporter: null,
    resolution: null,
    stable_at: null,
    status: null,
    storage: null,
    tags: [],
    tasks: [],
    terms: [],
    ticket: null,
    title: null,
    visibility: null,
    workflow_instances: null,
    loading: false,
    currentEvent: {},
  }
}

const getDefaultReportState = () => {
  return {
    type: "tactical",
    tactical: {
      conditions: null,
      actions: null,
      needs: null,
    },
    executive: {
      current_status: null,
      overview: null,
      next_steps: null,
    },
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showDeleteDialog: false,
    showEditSheet: false,
    showExport: false,
    showHandoffDialog: false,
    showNewSheet: false,
    showReportDialog: false,
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
        reporter: [],
        commander: null,
        incident_type: [],
        incident_priority: [],
        incident_severity: [],
        status: [],
        tag: [],
        tag_all: [],
        project: [],
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
    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "Incident"
    )
    return IncidentApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  get({ commit, state }) {
    // noop if no selected id available
    if (state.selected.id) {
      return IncidentApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
      })
    }
  },
  getDetails({ commit, state }, payload) {
    commit("SET_SELECTED_LOADING", true)
    if ("id" in payload) {
      return IncidentApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
      })
    } else if ("name" in payload) {
      // this is kinda dirty
      return IncidentApi.getAll({
        filter: JSON.stringify([
          { and: [{ model: "Incident", field: "name", op: "==", value: payload.name }] },
        ]),
      }).then((response) => {
        if (response.data.items.length) {
          // get the full data set
          return IncidentApi.get(response.data.items[0].id).then((response) => {
            commit("SET_SELECTED", response.data)
            commit("SET_SELECTED_LOADING", false)
          })
        } else {
          commit(
            "notification_backend/addBeNotification",
            {
              text: `Incident '${payload.name}' could not be found.`,
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
  showNewSheet({ commit }, incident) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", true)
    if (incident) {
      commit("SET_SELECTED", incident)
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
    router.push({ name: "IncidentTable" })
  },
  showDeleteDialog({ commit }, incident) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", incident)
  },
  closeDeleteDialog({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  showReportDialog({ commit }, incident) {
    commit("SET_DIALOG_REPORT", true)
    commit("SET_SELECTED", incident)

    state.report.tactical.actions +=
      "\n\nOutstanding Incident Tasks:\n" +
      incident.tasks.reduce((result, task) => {
        if (task.status == "Resolved") {
          return result
        }
        return (result ? result + "\n" : "") + "- " + task.description
      }, "")
  },
  closeReportDialog({ commit }) {
    commit("SET_DIALOG_REPORT", false)
    commit("RESET_SELECTED")
  },
  showExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", true)
  },
  closeExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", false)
  },
  showHandoffDialog({ commit }, value) {
    commit("SET_SELECTED", value)
    commit("SET_DIALOG_SHOW_HANDOFF", true)
  },
  closeHandoffDialog({ commit }) {
    commit("SET_DIALOG_SHOW_HANDOFF", false)
    commit("RESET_SELECTED")
  },
  showNewEditEventDialog({ commit }, event) {
    state.selected.currentEvent = event
    commit("SET_DIALOG_EDIT_EVENT", true)
  },
  closeEditEventDialog({ commit }) {
    commit("SET_DIALOG_EDIT_EVENT", false)
  },
  showNewPreEventDialog({ commit }, started_at) {
    started_at = moment(started_at).subtract(1, "seconds").toISOString()
    state.selected.currentEvent = { started_at, description: "", uuid: "" }
    commit("SET_DIALOG_EDIT_EVENT", true)
  },
  showNewEventDialog({ commit }, started_at) {
    started_at = moment(started_at).add(1, "seconds").toISOString()
    state.selected.currentEvent = { started_at, description: "", uuid: "" }
    commit("SET_DIALOG_EDIT_EVENT", true)
  },
  showDeleteEventDialog({ commit }, event) {
    state.selected.currentEvent = event
    commit("SET_DIALOG_DELETE_EVENT", true)
  },
  togglePin({ commit }, event) {
    state.selected.currentEvent = event
    state.selected.currentEvent.pinned = !state.selected.currentEvent.pinned
    IncidentApi.updateEvent(state.selected.id, state.selected.currentEvent).then(() => {
      IncidentApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
      })
      commit(
        "notification_backend/addBeNotification",
        { text: "Event updated successfully.", type: "success" },
        { root: true }
      )
    })
    commit("SET_DIALOG_EDIT_EVENT", false)
  },
  exportDoc({ commit }, timeline_filters) {
    IncidentApi.exportTimeline(state.selected.id, timeline_filters).then((response) => {
      commit("SET_SELECTED", response.data)
    })
    commit(
      "notification_backend/addBeNotification",
      { text: "Data exported successfully. This may take a few minutes.", type: "success" },
      { root: true }
    )
    commit("SET_DIALOG_EDIT_EVENT", false)
  },

  closeDeleteEventDialog({ commit }) {
    commit("SET_DIALOG_DELETE_EVENT", false)
  },
  storeNewEvent({ commit }) {
    IncidentApi.createNewEvent(state.selected.id, {
      source: "Incident Participant",
      description: state.selected.currentEvent.description,
      started_at: state.selected.currentEvent.started_at,
      type: "Custom event",
      details: {},
    }).then(() => {
      IncidentApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
      })
      commit(
        "notification_backend/addBeNotification",
        { text: "Event created successfully.", type: "success" },
        { root: true }
      )
    })
    commit("SET_DIALOG_EDIT_EVENT", false)
  },
  updateExistingEvent({ commit }) {
    IncidentApi.updateEvent(state.selected.id, state.selected.currentEvent).then(() => {
      IncidentApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
      })
      commit(
        "notification_backend/addBeNotification",
        { text: "Event updated successfully.", type: "success" },
        { root: true }
      )
    })
    commit("SET_DIALOG_EDIT_EVENT", false)
  },
  deleteEvent({ commit }) {
    IncidentApi.deleteEvent(state.selected.id, state.selected.currentEvent.uuid).then(() => {
      IncidentApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
      })
      commit(
        "notification_backend/addBeNotification",
        { text: "Event deleted successfully.", type: "success" },
        { root: true }
      )
    })
    commit("SET_DIALOG_DELETE_EVENT", false)
  },
  report({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return IncidentApi.create(state.selected)
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
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (Array.isArray(state.selected.reporter)) {
      state.selected.reporter = state.selected.reporter[0]
    }
    if (Array.isArray(state.selected.commander)) {
      state.selected.commander = state.selected.commander[0]
    }
    if (!state.selected.id) {
      return IncidentApi.create(state.selected)
        .then(() => {
          dispatch("closeNewSheet")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return IncidentApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeEditSheet")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident updated successfully.", type: "success" },
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
    return IncidentApi.bulkUpdate(state.table.rows.selected, payload)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Incident(s) updated successfully.", type: "success" },
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
    return IncidentApi.bulkDelete(state.table.rows.selected)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Incident(s) deleted successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(() => {
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  deleteIncident({ commit, dispatch }) {
    return IncidentApi.delete(state.selected.id).then(function () {
      dispatch("closeDeleteDialog")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Incident deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
  createReport({ commit, dispatch }) {
    return IncidentApi.createReport(
      state.selected.id,
      state.report.type,
      state.report[state.report.type]
    ).then(function () {
      dispatch("closeReportDialog")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Report created successfully.", type: "success" },
        { root: true }
      )
    })
  },
  createAllResources({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return IncidentApi.createAllResources(state.selected.id)
      .then(() => {
        IncidentApi.get(state.selected.id).then((response) => {
          commit("SET_SELECTED", response.data)
          dispatch("getEnabledPlugins").then((enabledPlugins) => {
            // Poll the server for resource creation updates.
            var interval = setInterval(function () {
              if (
                state.selected.conversation ^ enabledPlugins.includes("conversation") ||
                state.selected.documents ^ enabledPlugins.includes("document") ||
                state.selected.storage ^ enabledPlugins.includes("storage") ||
                state.selected.conference ^ enabledPlugins.includes("conference") ||
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
  resetSelected({ commit }) {
    commit("RESET_SELECTED")
  },
  joinIncident({ commit }, incidentId) {
    IncidentApi.join(incidentId, {}).then(() => {
      commit(
        "notification_backend/addBeNotification",
        { text: "You have successfully joined the incident.", type: "success" },
        { root: true }
      )
    })
  },
  subscribeToIncident({ commit }, incidentId) {
    IncidentApi.subscribe(incidentId, {}).then(() => {
      commit(
        "notification_backend/addBeNotification",
        {
          text: "You have successfully subscribed to the incident. You will receive all tactical reports about this incident via email.",
          type: "success",
        },
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
}

const mutations = {
  updateField,
  addIncidentCost(state, value) {
    state.selected.incident_costs.push(value)
  },
  removeIncidentCost(state, idx) {
    state.selected.incident_costs.splice(idx, 1)
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
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showDeleteDialog = value
  },
  SET_DIALOG_EDIT_EVENT(state, value) {
    state.dialogs.showEditEventDialog = value
  },
  SET_DIALOG_DELETE_EVENT(state, value) {
    state.dialogs.showDeleteEventDialog = value
  },
  SET_DIALOG_REPORT(state, value) {
    state.dialogs.showReportDialog = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
    state.report = Object.assign(state.report, getDefaultReportState())
  },
  SET_BULK_EDIT_LOADING(state, value) {
    state.table.bulkEditLoading = value
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  },
  SET_DEFAULT_PROJECT(state, value) {
    state.default_project = value
  },
  SET_CURRENT_USER_ROLE(state, value) {
    state.current_user_role = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
