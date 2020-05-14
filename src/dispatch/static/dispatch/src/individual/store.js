import IndividualApi from "@/individual/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

const getDefaultSelectedState = () => {
  return {
    name: null,
    email: null,
    company: null,
    notes: null,
    title: null,
    terms: [],
    incident_priorities: [],
    incident_types: [],
    is_external: null,
    is_active: null,
    id: null,
    created_at: null,
    updated_at: null,
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
      descending: [false]
    },
    loading: false
  }
}

const getters = {
  getField
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", true)
    return IndividualApi.getAll(state.table.options)
      .then(response => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, individual) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (individual) {
      commit("SET_SELECTED", individual)
    }
  },
  removeShow({ commit }, individual) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", individual)
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
      return IndividualApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "Individual created successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Individual not created. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    } else {
      return IndividualApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "Individual updated successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Individual not updated. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return IndividualApi.delete(state.selected.id)
      .then(() => {
        dispatch("closeRemove")
        dispatch("getAll")
        commit("app/SET_SNACKBAR", { text: "Individual deleted successfully." }, { root: true })
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Individual not deleted. Reason: " + err.response.data.detail,
            color: "red"
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
