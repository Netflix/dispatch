import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"

const getDefaultSelectedState = () => {
  return {
    expression: null,
    description: null,
    name: null,
    action: null,
    expiration: null,
    window: 5,
    loading: false,
    previewRows: {
      items: [],
      total: null,
    },
    previewRowsLoading: false,
    step: 1,
    filters: {
      tag: [],
      tag_type: [],
      project: [],
    },
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
      itemsPerPage: 10,
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
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "signal")
    return SignalApi.getAllInstances(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, signal) {
    if (signal) {
      commit("SET_SELECTED", signal)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  removeShow({ commit }, signal) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", signal)
  },
  closeCreateEdit({ commit }) {
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
