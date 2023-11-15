import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import NotificationApi from "@/notification/api"
import ProjectApi from "@/project/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    name: null,
    description: null,
    type: "conversation",
    target: null,
    project: null,
    enabled: null,
    evergreen: null,
    evergreen_owner: null,
    evergreen_reminder_interval: null,
    filters: [],
    loading: false,
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
      sortBy: ["created_at"],
      descending: [true],
      filters: {
        project: [],
      },
    },
    loading: false,
  },
  dailyReports: null,
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "Notification"
    )
    ProjectApi.getAll({ q: state.table.options.filters.project[0].name }).then((response) => {
      const project = response.data.items[0]
      if (project) {
        commit("SET_DAILY_REPORT_STATE", project.send_daily_reports ?? true)
      }
    })
    return NotificationApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
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
  updateDailyReports({ commit }, value) {
    ProjectApi.getAll({ q: state.table.options.filters.project[0].name }).then((response) => {
      const project = response.data.items[0]
      if (project) {
        project.send_daily_reports = value
        ProjectApi.update(project.id, project).then(() => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: `Project setting updated.`,
              type: "success",
            },
            { root: true }
          )
        })
      }
    })
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
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return NotificationApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Notification created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return NotificationApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Notification updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return NotificationApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Notification deleted successfully.", type: "success" },
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
  SET_DAILY_REPORT_STATE(state, value) {
    state.dailyReports = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
