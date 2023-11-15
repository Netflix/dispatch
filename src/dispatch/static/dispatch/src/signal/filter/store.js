import { getField, updateField } from "vuex-map-fields"
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
}

const getters = {
  getField,
  tableOptions({ state }) {
    // format our filters
    return state.table.options
  },
}

const actions = {
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
        .catch(() => {
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
        .catch(() => {
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
