import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentRoleApi from "@/incident_role/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    project: null,
    enabled: true,
    loading: false,
  }
}

export const incidentRoleTypes = [
  {
    type: "dispatch-incident-role-commander",
    title: "Commander",
    description: "Create a new commander policy.",
    icon: "mdi-shield-account",
  },
  {
    resource_type: "dispatch-incident-role-liason",
    title: "Liason",
    description: "Create a new liason policy.",
    icon: "mdi-account-tie",
  },
  {
    resource_type: "dispatch-incident-role-scribe",
    title: "Scribe",
    description: "Create a new scribe policy.",
    icon: "mdi-account-edit",
  },
]

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
      sortBy: ["name"],
      descending: [true],
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
    return IncidentRoleApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, incidentRole) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (incidentRole) {
      commit("SET_SELECTED", incidentRole)
    }
  },
  removeShow({ commit }, incidentRole) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", incidentRole)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return IncidentRoleApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("SET_SELECTED_LOADING", false)
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident role created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return IncidentRoleApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("SET_SELECTED_LOADING", false)
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident role updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return IncidentRoleApi.delete(state.selected.id)
      .then(function () {
        commit("SET_SELECTED_LOADING", false)
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Incident role deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
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
    // do not reset project
    let project = state.selected.project
    state.selected = { ...getDefaultSelectedState() }
    state.selected.project = project
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
