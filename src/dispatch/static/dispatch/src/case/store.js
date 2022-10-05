import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import CaseApi from "@/case/api"
import router from "@/router"

const getDefaultSelectedState = () => {
  return {
    assignee: null,
    case_priority: null,
    case_severity: null,
    case_type: null,
    closed_at: null,
    description: null,
    documents: [],
    duplicates: [],
    escalated_at: null,
    events: [],
    groups: [],
    signals: [],
    id: null,
    incidents: [],
    name: null,
    project: null,
    related: [],
    reported_at: null,
    resolution: null,
    status: null,
    storage: null,
    tags: [],
    ticket: null,
    title: null,
    triage_at: null,
    visibility: null,
    // workflow_instances: null,
    loading: false,
  }
}

const getDefaultReportState = () => {
  return {}
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showDeleteDialog: false,
    showEditSheet: false,
    showExport: false,
    showNewSheet: false,
    showEscalateDialog: false,
  },
  report: {
    ...getDefaultReportState(),
  },
  table: {
    rows: {
      items: [],
      total: null,
      selected: [],
    },
    options: {
      filters: {
        assignee: [],
        case_priority: [],
        case_severity: [],
        case_type: [],
        project: [],
        status: [],
        tag: [],
        tag_type: [],
        reported_at: {
          start: null,
          end: null,
        },
        closed_at: {
          start: null,
          end: null,
        },
      },
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["reported_at"],
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
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Case")
    return CaseApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  get({ commit, state }) {
    return CaseApi.get(state.selected.id).then((response) => {
      commit("SET_SELECTED", response.data)
    })
  },
  getDetails({ commit, state }, payload) {
    commit("SET_SELECTED_LOADING", true)
    if ("id" in payload) {
      return CaseApi.get(state.selected.id).then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
      })
    } else if ("name" in payload) {
      // this is kinda dirty
      return CaseApi.getAll({
        filter: JSON.stringify([
          { and: [{ model: "Case", field: "name", op: "==", value: payload.name }] },
        ]),
      }).then((response) => {
        if (response.data.items.length) {
          commit("SET_SELECTED", response.data.items[0])
        } else {
          commit(
            "notification_backend/addBeNotification",
            {
              text: `Case '${payload.name}' could not be found.`,
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
  showNewSheet({ commit }, value) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", true)
    if (value) {
      commit("SET_SELECTED", value)
    }
  },
  closeNewSheet({ commit }) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", false)
    commit("RESET_SELECTED")
  },
  showEditSheet({ commit }) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", true)
  },
  closeEditSheet({ commit }) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", false)
    commit("RESET_SELECTED")
    router.push({ name: "CaseTable" })
  },
  showDeleteDialog({ commit }, value) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", value)
  },
  closeDeleteDialog({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  showEscalateDialog({ commit }, value) {
    commit("SET_DIALOG_ESCALATE", true)
    commit("SET_SELECTED", value)
  },
  closeEscalateDialog({ commit }) {
    commit("SET_DIALOG_ESCALATE", false)
    commit("RESET_SELECTED")
    commit("incident/RESET_SELECTED", null, { root: true })
  },
  showExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", true)
  },
  closeExport({ commit }) {
    commit("SET_DIALOG_SHOW_EXPORT", false)
  },
  escalate({ commit, dispatch }, payload) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.escalate(state.selected.id, payload).then((response) => {
      commit("incident/SET_SELECTED", response.data, { root: true })
      commit("SET_SELECTED_LOADING", false)
      this.interval = setInterval(function () {
        if (state.selected.id) {
          dispatch("incident/get", response.data.id, { root: true })
        }

        // TODO this is fragile but we don't set anything as "created"
        if (state.selected.conversation) {
          clearInterval(this.interval)
        }
      }, 5000)
    })
  },
  report({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    return CaseApi.create(state.selected)
      .then((response) => {
        commit("SET_SELECTED", response.data)
        commit("SET_SELECTED_LOADING", false)
        this.interval = setInterval(function () {
          if (state.selected.id) {
            dispatch("get")
          }

          // TODO this is fragile but we don't set anything as "created"
          if (state.selected.conversation) {
            clearInterval(this.interval)
          }
        }, 5000)
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return CaseApi.create(state.selected)
        .then(() => {
          dispatch("closeNewSheet")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Case created successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return CaseApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeEditSheet")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Case updated successfully.", type: "success" },
            { root: true }
          )
          commit("SET_SELECTED_LOADING", false)
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  saveBulk({ commit, dispatch }, payload) {
    commit("SET_BULK_EDIT_LOADING", true)
    return CaseApi.bulkUpdate(state.table.rows.selected, payload)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Case(s) updated successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(() => {
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  deleteBulk({ commit, dispatch }) {
    commit("SET_BULK_EDIT_LOADING", true)
    return CaseApi.bulkDelete(state.table.rows.selected)
      .then(() => {
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Case(s) deleted successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(() => {
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  deleteCase({ commit, dispatch }) {
    return CaseApi.delete(state.selected.id).then(function () {
      dispatch("closeDeleteDialog")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Case deleted successfully.", type: "success" },
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
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    // reset selected on table load
    value["selected"] = []
    state.table.rows = value
  },
  SET_DIALOG_SHOW_EDIT_SHEET(state, value) {
    state.dialogs.showEditSheet = value
  },
  SET_DIALOG_SHOW_NEW_SHEET(state, value) {
    state.dialogs.showNewSheet = value
  },
  SET_DIALOG_SHOW_EXPORT(state, value) {
    state.dialogs.showExport = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showDeleteDialog = value
  },
  SET_DIALOG_ESCALATE(state, value) {
    state.dialogs.showEscalateDialog = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_BULK_EDIT_LOADING(state, value) {
    state.table.bulkEditLoading = value
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
