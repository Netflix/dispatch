import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import PluginApi from "@/plugin/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    enabled: null,
    configuration: [],
    project: null,
    plugin: null,
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
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
      sortBy: ["Plugin.slug"],
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
    return PluginApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  getAllInstances: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options })
    return PluginApi.getAllInstances(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, plugin) {
    commit("SET_DIALOG_EDIT", true)
    if (plugin) {
      commit("SET_SELECTED", plugin)
    }
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_EDIT", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return PluginApi.createInstance(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAllInstances")
          commit(
            "notification_backend/addBeNotification",
            { text: "Plugin instance created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit("SET_SELECTED_LOADING", false)
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Plugin instance not created. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    } else {
      return PluginApi.updateInstance(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAllInstances")
          commit(
            "notification_backend/addBeNotification",
            { text: "Plugin instance updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit("SET_SELECTED_LOADING", false)
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Plugin instance not updated. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return PluginApi.delete(state.selected.id)
      .then(function () {
        dispatch("closeRemove")
        dispatch("getAllInstances")
        commit(
          "notification_backend/addBeNotification",
          { text: "Plugin instance deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch((err) => {
        commit(
          "notification_backend/addBeNotification",
          {
            text: "Plugin instance not deleted. Reason: " + err.response.data.detail,
            type: "error",
          },
          { root: true }
        )
      })
  },
}

const mutations = {
  updateField,
  addConfigurationItem(state) {
    state.selected.configuration.push({ key: null, value: null })
  },
  removeConfigurationItem(state, idx) {
    state.selected.configuration.splice(idx)
  },
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
  SET_DIALOG_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
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
