import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentPriorityApi from "@/incident/priority/api"
import ProjectApi from "@/project/api"

const getDefaultSelectedState = () => {
  return {
    color: null,
    default: false,
    description: null,
    enabled: false,
    executive_report_reminder: null,
    id: null,
    loading: false,
    name: null,
    page_commander: null,
    project: null,
    tactical_report_reminder: null,
    view_order: null,
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
      sortBy: ["view_order"],
      descending: [false],
      filters: {
        project: [],
      },
    },
    loading: false,
  },
  stablePriority: null,
}

const getters = {
  getField,
}

// debounce setting changes
var oldStablePriority = undefined

function commitStablePriority(commit, value) {
  ProjectApi.getAll({ q: state.table.options.filters.project[0].name }).then((response) => {
    const project = response.data.items[0]
    if (project) {
      project.stable_priority_id = value
      ProjectApi.update(project.id, project).then(() => {
        commit(
          "notification_backend/addBeNotification",
          {
            text: `Setting updated.`,
            type: "success",
          },
          { root: true }
        )
      })
    }
  })
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "IncidentPriority"
    )
    return IncidentPriorityApi.getAll(params)
      .then((response) => {
        if (response.data.items[0]) {
          ProjectApi.get(response.data.items[0].project.id).then((response) => {
            state.stablePriority = response.data.stable_priority
            oldStablePriority = state.stablePriority
          })
        }
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, incidentPriority) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (incidentPriority) {
      commit("SET_SELECTED", incidentPriority)
    }
  },
  removeShow({ commit }, incidentPriority) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", incidentPriority)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, state, dispatch }) {
    commit("SET_SELECTED_LOADING", true)

    if (!state.selected.id) {
      return IncidentPriorityApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident priority created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return IncidentPriorityApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Incident priority updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return IncidentPriorityApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Incident priority deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
  updateStablePriority({ commit }, value) {
    if (!value) state.stablePriority = null
    if (oldStablePriority === undefined) {
      oldStablePriority = state.stablePriority
      return
    }
    if (oldStablePriority?.name !== state.stablePriority?.name) {
      oldStablePriority = state.stablePriority
      if (value) {
        commitStablePriority(commit, state.stablePriority.id)
      } else {
        commitStablePriority(commit, null)
      }
    }
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
