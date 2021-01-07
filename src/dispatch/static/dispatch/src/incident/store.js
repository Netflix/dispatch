import IncidentApi from "@/incident/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce, forEach, each, has } from "lodash"

const getDefaultSelectedState = () => {
  return {
    commander: null,
    conference: null,
    conversation: null,
    created_at: null,
    description: null,
    documents: null,
    events: null,
    id: null,
    incident_priority: null,
    incident_type: null,
    name: null,
    participants: null,
    reported_at: null,
    reporter: null,
    stable_at: null,
    status: null,
    storage: null,
    tags: [],
    terms: [],
    ticket: null,
    duplicates: [],
    workflow_instances: null,
    title: null,
    visibility: null,
    trackingOnly: null,
    loading: false
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState()
  },
  dialogs: {
    showDeleteDialog: false,
    showEditSheet: false,
    showExport: false,
    showNewSheet: false
  },
  table: {
    rows: {
      items: [],
      total: null,
      selected: []
    },
    options: {
      filters: {
        reporter: [],
        commander: [],
        incident_type: [],
        incident_priority: [],
        status: [],
        tag: []
      },
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["reported_at"],
      descending: [true]
    },
    loading: false,
    bulkEditLoading: false
  }
}

const getters = {
  getField,
  tableOptions({ state }) {
    // format our filters
    return state.table.options
  }
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")

    let tableOptions = Object.assign({}, state.table.options)
    delete tableOptions.filters

    tableOptions.fields = []
    tableOptions.ops = []
    tableOptions.values = []

    forEach(state.table.options.filters, function(value, key) {
      each(value, function(value) {
        if (has(value, "id")) {
          tableOptions.fields.push(key + ".id")
          tableOptions.values.push(value.id)
        } else {
          tableOptions.fields.push(key)
          tableOptions.values.push(value)
        }
        tableOptions.ops.push("==")
      })
    })
    return IncidentApi.getAll(tableOptions)
      .then(response => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  get({ commit, state }) {
    return IncidentApi.get(state.selected.id).then(response => {
      commit("SET_SELECTED", response.data)
    })
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
  showEditSheet({ commit }, incident) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", true)
    if (incident) {
      commit("SET_SELECTED", incident)
    }
  },
  closeEditSheet({ commit }) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", false)
    commit("RESET_SELECTED")
  },
  showDeleteDialog({ commit }, incident) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", incident)
  },
  closeDeleteDialog({ commit }) {
    commit("SET_DIALOG_DELETE", false)
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
    if (state.selected.trackingOnly === true) {
      state.selected.status = "Closed"
    }
    return IncidentApi.create(state.selected)
      .then(response => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
        this.interval = setInterval(function() {
          if (state.selected.id) {
            dispatch("get")
          }

          // TODO this is fragile but we don't set anything as "created"
          if (state.selected.conversation) {
            clearInterval(this.interval)
          }
        }, 5000)
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text:
              "Incident could not be reported. Please try again. Reason: " +
              err.response.data.detail,
            type: "error"
          },
          { root: true }
        )
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
            "app/SET_SNACKBAR",
            { text: "Incident created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Incident not updated. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return IncidentApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeEditSheet")
          dispatch("getAll")
          commit(
            "app/SET_SNACKBAR",
            { text: "Incident updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Incident not updated. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
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
          "app/SET_SNACKBAR",
          { text: "Incident(s) updated successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Incident(s) not updated. Reason: " + err.response.data.detail,
            type: "error"
          },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  deleteIncident({ commit, dispatch }) {
    return IncidentApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeDeleteDialog")
        dispatch("getAll")
        commit(
          "app/SET_SNACKBAR",
          { text: "Incident deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Incident not deleted. Reason: " + err.response.data.detail,
            type: "error"
          },
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
        "app/SET_SNACKBAR",
        { text: "You have successfully joined the incident.", type: "success" },
        { root: true }
      )
    })
  }
}

const mutations = {
  updateField,
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
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_BULK_EDIT_LOADING(state, value) {
    state.table.bulkEditLoading = value
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
