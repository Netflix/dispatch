import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import FormsTypeApi from "@/forms/types/api"
import FormsApi from "@/forms/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    created_at: null,
    updated_at: null,
    incident_id: null,
    form_type_id: null,
    form_data: null,
    status: null,
    attorney_status: "Not reviewed",
    attorney_questions: null,
    attorney_analysis: null,
    form_type: null,
    project: null,
    form_schema: null,
    attorney_form_schema: null,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showDeleteDialog: false,
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
        forms_type: null,
      },
    },
    loading: false,
  },
  form_types: [],
  current_page: 1,
  page_schema: null,
  incident_id: null,
  project_id: null,
}

const getters = {
  getField,
}

function createPayload() {
  const payload = {}
  const validKeys = [
    "id",
    "form_data",
    "status",
    "attorney_status",
    "attorney_questions",
    "attorney_analysis",
    "incident_id",
    "form_type_id",
  ]
  Object.keys(state.selected).forEach((key) => {
    if (validKeys.includes(key)) payload[key] = state.selected[key]
  })
  payload["form_data"] = JSON.stringify(payload["form_data"])
  payload["project_id"] = state.selected.project.id
  return payload
}

function save({ commit, dispatch }) {
  commit("SET_SELECTED_LOADING", true)
  if (!state.selected.id) {
    return FormsApi.create(createPayload(state.selected))
      .then(() => {
        commit("SET_DIALOG_CREATE_EDIT", false)
        dispatch("getAll")
        commit("SET_SELECTED_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Form type created successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  } else {
    return FormsApi.update(
      state.selected.id,
      state.selected.creator.id,
      createPayload(state.selected)
    )
      .then(() => {
        commit("SET_DIALOG_CREATE_EDIT", false)
        dispatch("getAll")
        commit("SET_SELECTED_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Form type updated successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  }
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Forms")
    commit("SET_TABLE_LOADING", "primary")
    FormsApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_ROWS", response.data)
        return FormsTypeApi.getAll()
          .then((response) => {
            commit("SET_TABLE_LOADING", false)
            commit("SET_FORM_TYPES", response.data)
          })
          .catch(() => {
            commit("SET_TABLE_LOADING", false)
          })
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createShow({ commit }, form_type_id) {
    commit("SET_SELECTED", { ...getDefaultSelectedState() })
    state.selected.form_type_id = form_type_id
    FormsTypeApi.get(form_type_id)
      .then((response) => {
        commit("SET_FORM_TYPE", response.data)
        commit("SET_DIALOG_CREATE_EDIT", true)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  },
  editShow({ commit }, selected) {
    commit("SET_SELECTED", selected)
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  showDeleteDialog({ commit }, form) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", form)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeDeleteDialog({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  saveAsDraft({ commit, dispatch }) {
    state.selected.status = "Draft"
    save({ commit, dispatch })
  },
  saveAsCompleted({ commit, dispatch }) {
    state.selected.status = "Completed"
    save({ commit, dispatch })
  },
  remove({ commit, dispatch }) {
    return FormsTypeApi.delete(state.selected.id, state.selected.creator.id)
      .then(function () {
        commit("SET_SELECTED_LOADING", false)
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "Form type deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(() => {
        commit("SET_SELECTED_LOADING", false)
      })
  },
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_FORM_SCHEMA(state, value) {
    state.selected.form_schema = value
  },
  SET_PAGE_SCHEMA(state, value) {
    state.page_schema = value
  },
  SET_FORM_TYPE(state, value) {
    state.selected.form_type = value
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
  SET_FORM_TYPES(state, value) {
    state.form_types = value.items
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showDeleteDialog = value
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
