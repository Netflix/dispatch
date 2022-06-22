import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentApi from "@/incident/api"
import router from "@/router"

const getDefaultSelectedState = () => {
  return {
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
    incident_type: null,
    name: null,
    participants: null,
    project: null,
    resolution: null,
    reported_at: null,
    reporter: null,
    stable_at: null,
    status: null,
    storage: null,
    tags: [],
    terms: [],
    ticket: null,
    title: null,
    visibility: null,
    workflow_instances: null,
    loading: false,
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
    showReportDialog: false,
    showEditSheet: false,
    showExport: false,
    showNewSheet: false,
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
        commander: [],
        incident_type: [],
        incident_priority: [],
        status: [],
        tag: [],
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
      },
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["reported_at"],
      descending: [true],
    },
    loading: false,
    bulkEditLoading: false,
  },
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
    return IncidentApi.get(state.selected.id).then((response) => {
      commit("SET_SELECTED", response.data)
    })
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
          commit("SET_SELECTED", response.data.items[0])
        } else {
          commit(
            "notification_backend/addBeNotification",
            {
              text: `Incident '${payload.name}' could not be found.`,
              type: "error",
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
  report({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return IncidentApi.create(state.selected)
      .then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
        this.interval = setInterval(function () {
          if (state.selected.id) {
            dispatch("get")
          }

          // TODO this is fragile but we don't set anything as "created"
          if (state.selected.conversation) {
            clearInterval(this.interval)
          }
        }, 5000)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
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
    console.log("C")
    IncidentApi.subscribe(incidentId, {}).then(() => {
      commit(
        "notification_backend/addBeNotification",
        {
          text: "You have successfully subscribed to the incident. You will recieve all incident tactical reports.",
          type: "success",
        },
        { root: true }
      )
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
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showDeleteDialog = value
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
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
