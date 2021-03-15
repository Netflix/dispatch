import OrganizationApi from "@/organization/api"

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
    return OrganizationApi.getAll(state.table.options)
      .then(response => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, organization) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (organization) {
      commit("SET_SELECTED", organization)
    }
  },
  removeShow({ commit }, organization) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", organization)
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
      return OrganizationApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Organization not created. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    } else {
      return OrganizationApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Organization not updated. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return OrganizationApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Organization deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(err => {
        commit(
          "notification_backend/addBeNotification",
          {
            text: "Organization not deleted. Reason: " + err.response.data.detail,
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
