import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import FeedbackApi from "@/feedback/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    incident: null,
    participant: null,
    rating: null,
    feedback: null,
    loading: false,
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
      sortBy: ["created_at"],
      descending: [true],
      filters: {
        incident: [],
        rating: [],
        feedback: [],
        participant: [],
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
    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "Feedback"
    )
    return FeedbackApi.getAll(params).then((response) => {
      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", response.data)
    })
  }, 500),
  createEditShow({ commit }, feedback) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (feedback) {
      commit("SET_SELECTED", feedback)
    }
  },
  removeShow({ commit }, feedback) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", feedback)
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
    if (!state.selected.id) {
      return FeedbackApi.create(state.selected).then(() => {
        dispatch("closeCreateEdit")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Feedback created successfully.", type: "success" },
          { root: true }
        )
      })
    } else {
      return FeedbackApi.update(state.selected.id, state.selected).then(() => {
        dispatch("closeCreateEdit")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Feedback updated successfully.", type: "success" },
          { root: true }
        )
      })
    }
  },
  remove({ commit, dispatch }) {
    return FeedbackApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Feedback deleted successfully.", type: "success" },
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
