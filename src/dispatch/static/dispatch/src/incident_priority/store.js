import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentPriorityApi from "@/incident_priority/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    name: null,
    page_commander: null,
    view_order: null,
    tactical_report_reminder: null,
    project: null,
    executive_report_reminder: null,
    description: null,
    loading: false,
    default: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showRemove: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["view_order"],
      descending: [false],
      filters: {
        project: [],
      },
    },
    loading: false,
  },
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options })
    return IncidentPriorityApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, incidentPriority) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (incidentPriority) {
      commit("SET_SELECTED", incidentPriority)
    }
  },
  removeShow({ commit }, incidentPriority) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", incidentPriority)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, state, dispatch }) {
    if (!state.selected.id) {
      return IncidentPriorityApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident priority created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Incident priority not created. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    } else {
      return IncidentPriorityApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident priority updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Incident priority not updated. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return IncidentPriorityApi.delete(state.selected.id)
      .then(function () {
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Incident priority deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch((err) => {
        commit(
          "notification_backend/addBeNotification",
          {
            text: "Incident priority not deleted. Reason: " + err.response.data.detail,
            type: "error",
          },
          { root: true }
        )
      })
  },
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
    state.table.rows = value
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
