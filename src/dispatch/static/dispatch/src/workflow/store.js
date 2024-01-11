import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import WorkflowApi from "@/workflow/api"

const getDefaultSelectedState = () => {
  return {
    description: null,
    enabled: null,
    resource_id: null,
    parameters: [],
    project: null,
    plugin_instance: null,
    name: null,
    id: null,
    loading: false,
    case: null,
    incident: null,
  }
}

const getDefaultSelectedInstanceState = () => {
  return {
    run_reason: null,
    id: null,
    parameters: [],
    workflow: { id: null },
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  selectedInstance: {
    ...getDefaultSelectedInstanceState(),
  },
  dialogs: {
    showCreateEdit: false,
    showRemove: false,
    showRun: false,
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
      descending: [false],
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
      { ...state.table.options },
      "Workflow"
    )
    return WorkflowApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, workflow) {
    if (workflow) {
      commit("SET_SELECTED", workflow)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  showRun({ commit }, payload) {
    commit("SET_DIALOG_RUN", true)
    if (payload.type === "incident") {
      commit("SET_SELECTED_INSTANCE_INCIDENT", payload.data)
    } else if (payload.type === "case") {
      commit("SET_SELECTED_INSTANCE_CASE", payload.data)
    } else if (payload.type === "signal") {
      commit("SET_SELECTED_INSTANCE_SIGNAL", payload.data)
    }
  },
  removeShow({ commit }, workflow) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", workflow)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeCreateEditDialog({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  closeRun({ commit }) {
    commit("SET_DIALOG_RUN", false)
    commit("RESET_SELECTED_INSTANCE")
  },
  run({ commit }) {
    let payload = { ...state.selectedInstance }
    commit("SET_SELECTED_INSTANCE_LOADING", true)
    return WorkflowApi.run(state.selectedInstance.workflow.id, payload)
      .then((response) => {
        commit("SET_SELECTED_INSTANCE_LOADING", false)
        commit("SET_SELECTED_INSTANCE", response.data)
        var interval = setInterval(function () {
          if (state.selectedInstance.id == null) {
            clearInterval(interval)
            return
          }
          WorkflowApi.getInstance(state.selectedInstance.id).then((response) => {
            commit("SET_SELECTED_INSTANCE", response.data)
          })

          if (state.selectedInstance.status == "Completed") {
            clearInterval(interval)
          }
        }, 5000)
        return response.data
      })
      .catch(() => {
        commit("SET_SELECTED_INSTANCE_LOADING", false)
        commit("RESET_SELECTED_INSTANCE")
      })
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return WorkflowApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Workflow created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return WorkflowApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Workflow updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return WorkflowApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Workflow deleted successfully.", type: "success" },
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
  SET_SELECTED_INSTANCE(state, value) {
    state.selectedInstance = Object.assign(state.selectedInstance, value)
  },
  SET_SELECTED_INSTANCE_LOADING(state, value) {
    state.selectedInstance.loading = value
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
  SET_DIALOG_RUN(state, value) {
    state.dialogs.showRun = value
  },
  SET_SELECTED_INSTANCE_CASE(state, value) {
    state.selectedInstance.case = value
  },
  SET_SELECTED_INSTANCE_INCIDENT(state, value) {
    state.selectedInstance.incident = value
  },
  SET_SELECTED_INSTANCE_SIGNAL(state, value) {
    state.selectedInstance.signal = value
  },
  RESET_SELECTED_INSTANCE(state) {
    // do not reset project
    state.selectedInstance = { ...getDefaultSelectedInstanceState() }
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
