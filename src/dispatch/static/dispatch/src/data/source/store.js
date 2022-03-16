import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import SourceApi from "@/data/source/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    loading: false,
    name: null,
    description: null,
    owner: null,
    retention: null,
    source_environment: null,
    source_status: null,
    source_type: null,
    source_transport: null,
    source_data_format: null,
    size: null,
    aggregated: null,
    delay: null,
    external_id: null,
    project: null,
    documentation: "",
    data_last_loaded_at: null,
    sampling_rate: null,
    schema: null,
    sample_log: null,
    cost: null,
    queries: [],
    links: [],
    incidents: [],
    alerts: [],
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
      sortBy: ["name"],
      descending: [true],
      filters: {
        tag: [],
        project: [],
        tag_type: [],
        source_environment: [],
        source_status: [],
        source_type: [],
        source_transport: [],
        source_data_format: [],
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
      {
        ...state.table.options,
      },
      "Source"
    )
    return SourceApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, source) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (source) {
      commit("SET_SELECTED", source)
    } else {
      commit("SET_SELECTED", getDefaultSelectedState())
    }
  },
  removeShow({ commit }, source) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", source)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
  },
  getDetails({ commit, state }, payload) {
    commit("SET_SELECTED_LOADING", true)
    if ("id" in payload) {
      return SourceApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
      })
    } else if ("name" in payload) {
      // this is kinda dirty
      return SourceApi.getAll({
        filter: JSON.stringify([
          {
            and: [
              {
                model: "Source",
                field: "name",
                op: "==",
                value: payload.name,
              },
            ],
          },
        ]),
      }).then((response) => {
        if (response.data.items.length) {
          commit("SET_SELECTED", response.data.items[0])
        } else {
          commit(
            "notification_backend/addBeNotification",
            {
              text: `Source '${payload.name}' could not be found.`,
              type: "error",
            },
            { root: true }
          )
          commit("SET_DIALOG_SHOW_EDIT_SHEET", false)
        }
        commit("SET_SELECTED_LOADING", false)
      })
    }
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return SourceApi.create(state.selected)
        .then(function (resp) {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Source created successfully.", type: "success" },
            { root: true }
          )
          return resp.data
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return SourceApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Source updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return SourceApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Source deleted successfully.", type: "success" },
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
  RESET_SELECTED(state) {
    state.selected = { ...getDefaultSelectedState() }
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
