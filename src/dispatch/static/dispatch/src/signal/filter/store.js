import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"
import SearchUtils from "@/search/utils"
import SignalFilterApi from "@/signal/filter/api"

const getDefaultSelectedState = () => {
  return {
    expression: null,
    description: null,
    name: null,
    action: "snooze",
    expiration: null,
    window: null,
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
      filters: {
        created_at: {
          start: null,
          end: null,
        },
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["created_at"],
      descending: [true],
    },
    loading: false,
  },
  snoozeTable: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {
        created_at: {
          start: null,
          end: null,
        },
        signal: [],
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["created_at"],
      descending: [true],
    },
    loading: false,
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
  // todo(amats): needs to be filtered for snoozes and not deduplications.
  getAllSnoozes: debounce(({ commit, state }) => {
    commit("SET_SNOOZE_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.snoozeTable.options })
    return SignalFilterApi.getAll(params)
      .then((response) => {
        commit("SET_SNOOZE_TABLE_LOADING", false)
        commit("SET_SNOOZE_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_SNOOZE_TABLE_LOADING", false)
      })
  }, 500),
  save({ commit, state }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return SignalFilterApi.create(state.selected)
        .then((resp) => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal filter created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
          commit("RESET_SELECTED")
          commit("SET_DIALOG_CREATE_EDIT", false)
          return resp.data
        })
        .catch((err) => {
          let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
          commit(
            "notification_backend/addBeNotification",
            { text: `Error trying to save: ${errorText}`, type: "exception" },
            { root: true }
          )
          commit("RESET_SELECTED")
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return SignalFilterApi.update(state.selected.id, state.selected)
        .then(() => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal filter updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch((err) => {
          let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
          commit(
            "notification_backend/addBeNotification",
            { text: `Error trying to save: ${errorText}`, type: "exception" },
            { root: true }
          )
          commit("RESET_SELECTED")
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  createEditShow({ commit }, signal) {
    if (signal) {
      commit("SET_SELECTED", signal)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  closeCreateEditDialog({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
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
  SET_SNOOZE_TABLE_LOADING(state, value) {
    state.snoozeTable.loading = value
  },
  SET_SNOOZE_TABLE_ROWS(state, value) {
    state.snoozeTable.rows = value
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
