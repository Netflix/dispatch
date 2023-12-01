import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import DataFormatApi from "@/data/source/dataFormat/api"

const getDefaultSelectedState = () => {
  return {
    loading: false,
    id: null,
    name: null,
    description: null,
    project: null,
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
      itemsPerPage: 25,
      sortBy: ["name"],
      descending: [true],
      filters: {
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
      {
        ...state.table.options,
      },
      "SourceDataFormat"
    )
    return DataFormatApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, environment) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (environment) {
      commit("SET_SELECTED", environment)
    }
  },
  removeShow({ commit }, environment) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", environment)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  getDetails({ commit, state }, payload) {
    commit("SET_SELECTED_LOADING", true)
    if ("id" in payload) {
      return DataFormatApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
      })
    } else if ("name" in payload) {
      // this is kinda dirty
      return DataFormatApi.getAll({
        filter: JSON.stringify([
          {
            and: [
              {
                model: "environment",
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
              text: `DataFormat '${payload.name}' could not be found.`,
              type: "exception",
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
      return DataFormatApi.create(state.selected)
        .then(function (resp) {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Dataformat created successfully.", type: "success" },
            { root: true }
          )
          return resp.data
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return DataFormatApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "DataFormat updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return DataFormatApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "DataFormat deleted successfully.", type: "success" },
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
