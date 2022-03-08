import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import DocumentApi from "@/document/api"

const getDefaultSelectedState = () => {
  return {
    name: null,
    resource_type: null,
    resource_id: null,
    weblink: null,
    description: null,
    id: null,
    filters: [],
    project: null,
    evergreen: null,
    evergreen_owner: null,
    evergreen_reminder_interval: null,
    created_at: null,
    updated_at: null,
    loading: false,
  }
}

export const templateDocumentTypes = [
  {
    resource_type: "dispatch-incident-document-template",
    title: "Incident",
    description: "Create a new incident template",
    icon: "mdi-file-document-edit-outline",
  },
  {
    resource_type: "dispatch-executive-report-document-template",
    title: "Executive",
    description: "Create a new executive template",
    icon: "mdi-text-box-check-outline",
  },
  {
    resource_type: "dispatch-incident-review-document-template",
    title: "Review",
    description: "Create a new incident review template",
    icon: "mdi-text-box-search-outline",
  },
  {
    resource_type: "dispatch-incident-tracking-template",
    title: "Tracking",
    description: "Create a new tracking template",
    icon: "mdi-file-document-multiple-outline",
  },
]

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
      itemsPerPage: 10,
      sortBy: ["name"],
      descending: [false],
      filters: {
        project: [],
        resource_type: templateDocumentTypes.map((item) => {
          return {
            model: "Document",
            field: "resource_type",
            value: item.resource_type,
          }
        }),
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

    let documentTypes = []
    for (const key in state.resourceTypes) {
      documentTypes.push({
        model: "Document",
        field: "resource_type",
        op: "==",
        value: key,
      })
    }

    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "Document",
      documentTypes
    )
    return DocumentApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, template) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (template) {
      commit("SET_SELECTED", template)
    }
  },
  removeShow({ commit }, document) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", document)
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
      return DocumentApi.create(state.selected)
        .then(function (resp) {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("SET_SELECTED_LOADING", false)
          commit(
            "notification_backend/addBeNotification",
            { text: "Document created successfully.", type: "success" },
            { root: true }
          )
          return resp.data
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return DocumentApi.update(state.selected.id, state.selected).then(() => {
        commit("SET_SELECTED_LOADING", false)
        dispatch("closeCreateEdit")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Document updated successfully.", type: "success" },
          { root: true }
        )
      })
    }
  },
  remove({ commit, dispatch }) {
    return DocumentApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Document deleted successfully.", type: "success" },
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
