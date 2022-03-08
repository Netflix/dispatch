import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import TaskApi from "@/task/api"

const getDefaultSelectedState = () => {
  return {
    resolved_at: null,
    resolve_by: null,
    creator: null,
    owner: null,
    assignees: [],
    description: null,
    incident: null,
    status: null,
    priority: null,
    project: null,
    source: null,
    id: null,
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
    showExport: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
      selected: [],
    },
    options: {
      filters: {
        creator: [],
        owner: [],
        assignee: [],
        incident: [],
        incident_type: [],
        incident_priority: [],
        status: [],
        project: [],
      },
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["status"],
      descending: [false],
    },
    loading: false,
    bulkEditLoading: false,
  },
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Task")
    return TaskApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, task) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (task) {
      commit("SET_SELECTED", task)
    }
  },
  removeShow({ commit }, task) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", task)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  showExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", true)
  },
  closeExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", false)
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return TaskApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Task created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return TaskApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Task updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  saveBulk({ commit, dispatch }, payload) {
    commit("SET_BULK_EDIT_LOADING", true)
    return TaskApi.bulkUpdate(state.table.rows.selected, payload)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Task(s) updated successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(() => {
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  remove({ commit, dispatch }) {
    return TaskApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Task deleted successfully.", type: "success" },
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
    // reset selected on table load
    value["selected"] = []
    state.table.rows = value
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_SHOW_EXPORT(state, value) {
    state.dialogs.showExport = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  SET_BULK_EDIT_LOADING(state, value) {
    state.table.bulkEditLoading = value
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
