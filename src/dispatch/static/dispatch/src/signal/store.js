import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"

const getDefaultSelectedState = () => {
  return {
    case_priority: null,
    case_type: null,
    conversation_target: null,
    create_case: true,
    created_at: null,
    description: null,
    enabled: false,
    engagements: [],
    entity_types: [],
    external_id: null,
    external_url: null,
    filters: [],
    genai_enabled: false,
    genai_model: null,
    genai_prompt: null,
    genai_system_message: null,
    id: null,
    lifecycle: null,
    loading: false,
    name: null,
    oncall_service: null,
    owner: null,
    project: null,
    runbook: null,
    signal_definition: null,
    source: null,
    tags: [],
    variant: null,
    workflow_instances: null,
    workflows: [],
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showRawSignalDialog: false,
    showRemove: false,
    showHistory: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {
        case_priority: [],
        case_severity: [],
        case_type: [],
        project: [],
        tag: [],
        tag_type: [],
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["name"],
      descending: [true],
    },
    loading: false,
    bulkEditLoading: false,
  },
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "signal")
    return SignalApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  get({ commit, state }) {
    return SignalApi.get(state.selected.id).then((response) => {
      commit("SET_SELECTED", response.data)
    })
  },
  createEditShow({ commit }, signal) {
    if (signal) {
      commit("SET_SELECTED", signal)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  showHistory({ commit }, signal) {
    if (signal) {
      commit("SET_SELECTED", signal)
    }
    commit("SET_DIALOG_HISTORY", true)
  },
  removeShow({ commit }, signal) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", signal)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  closeHistory({ commit }) {
    commit("SET_DIALOG_HISTORY", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return SignalApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal Definition created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return SignalApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal Definition updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return SignalApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Signal Definition deleted successfully.", type: "success" },
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
  SET_DIALOG_HISTORY(state, value) {
    state.dialogs.showHistory = value
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
