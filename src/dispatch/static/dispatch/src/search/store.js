import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchApi from "@/search/api"
import SearchUtils from "@/search/utils"

const getDefaultSelectedState = () => {
  return {
    description: null,
    expression: null,
    individuals: null,
    loading: false,
    name: null,
    notifications: null,
    project: null,
    services: null,
    subject: "incident",
    teams: null,
    type: null,
    previewRows: {
      items: [],
      total: null,
    },
    previewRowsLoading: false,
    step: 1,
    filters: {
      incident_type: [],
      case_type: [],
      case_priority: [],
      incident_priority: [],
      status: [],
      tag: [],
      tag_type: [],
      project: [],
      visibility: [],
    },
  }
}

const state = {
  table: {
    rows: {
      items: [],
      total: null,
      selected: [],
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["updated_at"],
      descending: [false],
      filters: {
        project: [],
      },
    },
    loading: false,
  },
  results: {
    incidents: [],
    cases: [],
    tasks: [],
    documents: [],
    tags: [],
    queries: [],
    sources: [],
  },
  query: "",
  type: ["Document", "Incident", "Case", "Tag", "Task", "Source", "Query"],
  dialogs: {
    showCreate: false,
    showRemove: false,
    showCreateEdit: false,
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
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "SearchFilter"
    )
    return SearchApi.getAllFilters(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  setQuery({ commit }, query) {
    commit("SET_QUERY", query)
  },
  setModels({ commit }, models) {
    commit("SET_MODELS", models)
  },
  getResults({ commit, state }) {
    commit("SET_LOADING", true)
    return SearchApi.search(state.query, state.type)
      .then((response) => {
        commit("SET_RESULTS", response.data.results)
        commit("SET_LOADING", false)
      })
      .catch(() => {
        commit("SET_LOADING", false)
      })
  },
  showCreateDialog({ commit }) {
    commit("SET_DIALOG_SHOW_CREATE", true)
  },
  closeCreateDialog({ commit }) {
    commit("SET_DIALOG_SHOW_CREATE", false)
  },
  save({ commit, dispatch }) {
    commit("SET_LOADING", true)
    if (!state.selected.id) {
      return SearchApi.create(state.selected)
        .then((resp) => {
          commit(
            "notification_backend/addBeNotification",
            { text: "Search filter created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_LOADING", false)
          commit("SET_DIALOG_SHOW_CREATE", false)
          return resp.data
        })
        .catch(() => {
          commit("SET_LOADING", false)
        })
    } else {
      return SearchApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Search filter updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_LOADING", false)
        })
        .catch(() => {
          commit("SET_LOADING", false)
        })
    }
  },
  removeShow({ commit }, search_filter) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", search_filter)
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  remove({ commit, dispatch }) {
    return SearchApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Search filter deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
  createEditShow({ commit }, search_filter) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (search_filter) {
      commit("SET_SELECTED", search_filter)
    }
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
}

const mutations = {
  updateField,
  SET_LOADING(state, value) {
    state.loading = value
  },
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  RESET_SELECTED(state) {
    // do not reset project
    let project = state.selected.project
    state.selected = { ...getDefaultSelectedState() }
    state.selected.project = project
  },
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    state.table.rows = value
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
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
