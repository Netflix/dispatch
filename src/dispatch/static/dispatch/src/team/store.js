import TeamApi from "@/team/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

const getDefaultSelectedState = () => {
  return {
    name: null,
    terms: [],
    incident_priorities: [],
    incident_types: [],
    id: null,
    created_at: null,
    updated_at: null,
    company: null,
    email: null,
    loading: false
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState()
  },
  dialogs: {
    showCreateEdit: false,
    showRemove: false
  },
  table: {
    rows: {
      items: [],
      total: null
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["name"],
      descending: [true]
    },
    loading: false
  }
}

const getters = {
  getField
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    return TeamApi.getAll(state.table.options).then(response => {
      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", response.data)
    })
  }, 200),
  createEditShow({ commit }, team) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (team) {
      commit("SET_SELECTED", team)
    }
  },
  removeShow({ commit }, team) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", team)
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
      return TeamApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification/addBeNotification",
            { text: "Team created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "notification/addBeNotification",
            {
              text: "Team not created. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    } else {
      return TeamApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification/addBeNotification",
            { text: "Team updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "notification/addBeNotification",
            {
              text: "Team not updated. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return TeamApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "notification/addBeNotification",
          { text: "Team deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(err => {
        commit(
          "notification/addBeNotification",
          {
            text: "Team not deleted. Reason: " + err.response.data.detail,
            type: "error"
          },
          { root: true }
        )
      })
  }
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
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
