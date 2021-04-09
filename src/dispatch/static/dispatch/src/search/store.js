import SearchApi from "@/search/api"
import { getField, updateField } from "vuex-map-fields"

const getDefaultSelectedState = () => {
  return {
    expression: null,
    description: null,
    name: null,
    type: null,
    loading: false,
    previewRows: {
      items: [],
      total: null,
    },
    previewRowsLoading: false,
    step: 1,
    filters: {
      incident_type: null,
      incident_priority: null,
      status: null,
      tags: null,
    },
  }
}

const state = {
  results: {
    incidents: [],
    tasks: [],
    documents: [],
    tags: [],
  },
  query: "",
  models: [],
  dialogs: {
    showCreate: false,
  },
  loading: false,
  selected: {
    ...getDefaultSelectedState(),
  },
}

const getters = {
  getField,
}

const actions = {
  setQuery({ commit }, query) {
    commit("SET_QUERY", query)
  },
  setModels({ commit }, models) {
    commit("SET_MODELS", models)
  },
  getResults({ commit, state }) {
    commit("SET_LOADING", false)
    return SearchApi.search(state.query, state.models)
      .then((response) => {
        commit("SET_RESULTS", response.data.results)
        commit("SET_LOADING", false)
      })
      .catch((err) => {
        commit(
          "notification_backend/addBeNotification",
          {
            text: "Search Failed. Reason: " + err.response.data.detail,
            color: "red",
          },
          { root: true }
        )
        commit("SET_LOADING", false)
      })
  },
  showCreateDialog({ commit }) {
    commit("SET_DIALOG_SHOW_CREATE", true)
  },
  closeCreateDialog({ commit }) {
    commit("SET_DIALOG_SHOW_CREATE", false)
  },
  save({ commit }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return SearchApi.create(state.selected)
        .then(() => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Search filter created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
          commit("SET_DIALOG_SHOW_CREATE", false)
          commit("RESET_SELECTED")
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Search Filter not saved. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return SearchApi.update(state.selected.id, state.selected)
        .then(() => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Search filter updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Search filter not updated. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
}

const mutations = {
  updateField,
  SET_LOADING(state, value) {
    state.loading = value
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  },
  SET_RESULTS(state, results) {
    state.results = results
  },
  SET_QUERY(state, query) {
    state.query = query
  },
  SET_MODELS(state, models) {
    state.models = models
  },
  SET_DIALOG_SHOW_CREATE(state, value) {
    state.dialogs.showCreate = value
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
