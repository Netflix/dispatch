import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import FormsTypeApi from "@/forms/types/api"
import FormsApi from "@/forms/api"
import { ref } from "vue"
import { be } from "date-fns/locale"

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
    memo_link: null,
    form_type: null,
    project: null,
    form_schema: [],
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
      itemsPerPage: -1,
      sortBy: ["created_at"],
      descending: [true],
      filters: {},
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

function getCurrentPage(form_schema) {
  // console.log(`**** Page was just requested - about to reconstruct from ${form_schema}`)
  let schema = JSON.parse(form_schema)
  let output_schema = []
  for (let item of schema) {
    let obj = {
      name: item.name,
      label: item.title,
      help: item.hint ? item.hint : null,
      if: item.if ? item.if : null,
    }
    if (item.type == "text") {
      obj = {
        $formkit: "text",
        ...obj,
      }
      output_schema.push(obj)
    }
    if (item.type == "boolean") {
      obj = {
        $formkit: "checkbox",
        ...obj,
      }
      output_schema.push(obj)
    }
    if (item.type == "select") {
      console.log(`**** The item multiple is ${item.multiple}`)
      if (item.multiple) {
        if (item.multiple == false) {
          obj = {
            $formkit: "checkbox",
            multiple: true,
            options: item.options,
            ...obj,
          }
        } else {
          obj = {
            $formkit: "select",
            multiple: true,
            options: item.options,
            ...obj,
            help: "Select all that apply by holding command (macOS) or control (PC).",
          }
        }
        output_schema.push(obj)
      } else {
        obj = {
          $formkit: "checkbox",
          options: item.options,
          validation: "max:1",
          ...obj,
        }
        output_schema.push(obj)
      }
    }
  }
  console.log(`**** Page was just requested - reconstructed to ${JSON.stringify(output_schema)}`)
  return output_schema
  return [
    {
      $formkit: "text",
      name: "email",
      prefixIcon: "email",
      label: "Email",
      value: "hello@formkit.com",
      help: "This email will be used for account notifications.",
      validation: "required|email",
    },
    {
      $formkit: "number",
      name: "users",
      prefixIcon: "avatarMan",
      id: "users",
      value: "3",
      label: "Users",
      help: "How many users do you need on your plan? http://formkit.com/pricing",
    },
    {
      $formkit: "checkbox",
      name: "eu_company",
      id: "eu",
      label: "Are you located in the European Union?",
    },
    {
      $formkit: "select",
      // 👀  Oooo, conditionals!
      if: "$get(eu).value",
      name: "cookie_notice",
      label: "Cookie notice frequency",
      prefixIcon: "warning",
      options: {
        refresh: "Every page load",
        hourly: "Ever hour",
        daily: "Every day",
      },
      help: "How often should we display a cookie notice?",
    },
  ]
}

function createPayload() {
  const payload = {}
  const validKeys = [
    "id",
    "form_data",
    "status",
    "attorney_status",
    "memo_link",
    "incident_id",
    "form_type_id",
  ]
  Object.keys(state.selected).forEach((key) => {
    if (validKeys.includes(key)) payload[key] = state.selected[key]
  })
  payload["form_data"] = JSON.stringify(payload["form_data"])
  console.log(`**** The form data is now : ${JSON.stringify(payload["form_data"])}`)
  payload["project_id"] = state.selected.project.id
  return payload
}

function save({ commit, dispatch }) {
  commit("SET_SELECTED_LOADING", true)
  if (!state.selected.id) {
    return FormsApi.create(createPayload(state.selected))
      .then(() => {
        console.log("**** Form created successfully")
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
        dispatch("forms_table/getAll", null, { root: true })
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
    let incidentFilter = [
      {
        model: "Incident",
        field: "id",
        op: "==",
        value: state.incident_id,
      },
    ]
    let filterOptions = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "Forms",
      incidentFilter
    )
    commit("SET_TABLE_LOADING", "primary")
    console.log(`**** Params: ${JSON.stringify(filterOptions)}`)
    let projectFilter = [
      {
        model: "Project",
        field: "id",
        op: "==",
        value: state.project_id,
      },
    ]
    let formsTypeFilter = SearchUtils.createParametersFromTableOptions(
      { ...state.table.options },
      "FormsType",
      projectFilter
    )
    commit("SET_TABLE_LOADING", "primary")
    console.log(`**** Params: ${JSON.stringify(filterOptions)}`)
    console.log(`**** Params: ${JSON.stringify(formsTypeFilter)}`)
    FormsApi.getAll(filterOptions)
      .then((response) => {
        commit("SET_TABLE_ROWS", response.data)
        return FormsTypeApi.getAll(formsTypeFilter)
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
        commit("SET_PAGE_SCHEMA", getCurrentPage(response.data.form_schema))
        commit("SET_FORM_TYPE", response.data)
        commit("SET_DIALOG_CREATE_EDIT", true)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  },
  editShow({ commit }, selected) {
    commit("SET_SELECTED", selected)
    // console.log(`**** Edit form type: ${JSON.stringify(selected)}`)
    commit("SET_PAGE_SCHEMA", getCurrentPage(selected.form_type.form_schema))
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  showDeleteDialog({ commit }, form) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", form)
  },
  closeCreateEdit({ commit }) {
    console.log(`**** CAlling closeCreateEdit`)
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
  deleteForm({ commit, dispatch }) {
    return FormsApi.delete(state.selected.id, state.selected.creator.id)
      .then(function () {
        commit("SET_SELECTED_LOADING", false)
        dispatch("closeDeleteDialog")
        dispatch("getAll")
        dispatch("forms_table/getAll", null, { root: true })
        commit(
          "notification_backend/addBeNotification",
          { text: "Form deleted successfully.", type: "success" },
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
    state.selected.form_data = JSON.parse(state.selected.form_data)
  },
  SET_FORM_SCHEMA(state, value) {
    console.log(`**** Got form schema: ${value}`)
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
