import { getField, updateField } from "vuex-map-fields"
import SignalEngagementApi from "@/signal/engagement/api"

const getDefaultSelectedState = () => {
  return {
    name: null,
    description: null,
    require_mfa: false,
    entity_type: null,
    message: null,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
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
    console.log("%O", state.selected)
    if (!state.selected.id) {
      return SignalEngagementApi.create(state.selected)
        .then((resp) => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal engagement created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
          commit("RESET_SELECTED")
          return resp.data
        })
        .catch((error) => {
          console.log(error)
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return SignalEngagementApi.update(state.selected.id, state.selected)
        .then(() => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal engagement updated successfully.", type: "success" },
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
