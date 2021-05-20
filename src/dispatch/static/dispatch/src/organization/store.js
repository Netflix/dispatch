import OrganizationApi from "@/organization/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

const getDefaultSelectedState = () => {
  return {
    name: null,
    description: [],
    id: null,
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreate: false,
  },
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    return OrganizationApi.getAll(state.table.options)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  showCreateDialog({ commit }, organization) {
    commit("SET_DIALOG_CREATE", true)
    if (organization) {
      commit("SET_SELECTED", organization)
    }
  },
  closeCreateDialog({ commit }) {
    commit("SET_DIALOG_CREATE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    if (!state.selected.id) {
      return OrganizationApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateDialog")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Organization not created. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    } else {
      return OrganizationApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateDialog")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Organization not updated. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    }
  },
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_DIALOG_CREATE(state, value) {
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
