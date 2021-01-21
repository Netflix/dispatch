import NotificationApi from "@/notification/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

const getDefaultSelectedState = () => {
  return {
    id: null,
    name: null,
    description: null,
    type: null,
    target: null,
    enabled: null,
    policy: null,
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
      sortBy: ["created_at"],
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
    return NotificationApi.getAll(state.table.options)
      .then(response => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, notification) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (notification) {
      commit("SET_SELECTED", notification)
    }
  },
  removeShow({ commit }, notification) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", notification)
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
      return NotificationApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Notification created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Notification not created. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    } else {
      return NotificationApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Notification updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Notification not updated. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return NotificationApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Notification deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(err => {
        commit(
          "notification_backend/addBeNotification",
          {
            text: "Notification not deleted. Reason: " + err.response.data.detail,
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
