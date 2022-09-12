import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    created_at: null,
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showExport: false,
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
    bulkEditLoading: false,
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
  showExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", true)
  },
  closeExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", false)
  },
}

const mutations = {
  updateField,
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    // reset selected on table load
    state.table.rows = value
  },
  SET_DIALOG_SHOW_EXPORT(state, value) {
    state.dialogs.showExport = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
