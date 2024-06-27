import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"
import { toUSD } from "@/filters"

import SearchUtils from "@/search/utils"
import FormsTypeApi from "@/forms/types/api"
import FormsApi from "@/forms/api"
import IncidentApi from "@/incident/api"

const hasFormkitPro = import.meta.env.VITE_FORMKIT_PRO_PROJECT_KEY

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
    attorney_form_data: null,
    scoring_schema: null,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showDeleteDialog: false,
    showAttorneyEdit: false,
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
  page_data: null,
  incident_id: null,
  project_id: null,
  incident_data: null,
  has_formkit_pro: hasFormkitPro,
  attorney_page_schema: null,
}

const getters = {
  getField,
}

function buildFormDoc(form_schema, form_data) {
  // Used to build the read-only answers given the questions in form_schema and the answers in form_data
  let schema = JSON.parse(form_schema)
  let data = JSON.parse(form_data)
  let output_qa = []
  for (let item of schema) {
    let name = item.name
    let label = item.title
    // find the key in form_data corresponding to this name
    let answer = data[name]
    if (answer && Array.isArray(answer) && answer.length == 0) {
      answer = ""
    }
    // add the label and answer to the output_qa array
    if (answer) {
      output_qa.push({
        question: label,
        answer,
      })
    }
  }
  return output_qa
}

function formatTacticalReport(tactical_report) {
  let output = ""
  if (tactical_report) {
    output = `Created: ${tactical_report.created_at}, Conditions: ${tactical_report.details.conditions}, Actions: ${tactical_report.details.actions}, Needs: ${tactical_report.details.needs}`
  }
  return output
}

function buildIncidentDoc(incident) {
  let output_qa = []
  if (incident) {
    output_qa.push({
      question: "Name",
      answer: incident.name,
    })
    output_qa.push({
      question: "Created At",
      answer: incident.created_at,
    })
    output_qa.push({
      question: "Description",
      answer: incident.description,
    })
    output_qa.push({
      question: "Type",
      answer: incident.incident_type.name,
    })
    output_qa.push({
      question: "Priority",
      answer: incident.incident_priority.name,
    })
    output_qa.push({
      question: "Status",
      answer: incident.status,
    })
    output_qa.push({
      question: "Severity",
      answer: incident.incident_severity.name,
    })
    output_qa.push({
      question: "Incident cost",
      answer: toUSD(incident.total_cost),
    })
    output_qa.push({
      question: "Last tactical report",
      answer: formatTacticalReport(incident.last_tactical_report),
    })
  }
  let incident_doc = ""
  for (let document of incident.documents) {
    if (document.resource_type == "dispatch-incident-document") {
      incident_doc = document.weblink
    }
  }
  return {
    data: output_qa,
    slack_channel: incident.conversation?.weblink,
    incident_doc: incident_doc,
    name: incident.name,
  }
}

function getCurrentPage(form_schema) {
  state.has_formkit_pro = hasFormkitPro
  let schema = JSON.parse(form_schema)
  let output_schema = []
  if (schema == null) {
    return output_schema
  }
  for (let item of schema) {
    let obj = {
      name: item.name,
      id: item.name,
      key: item.name,
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
    if (item.type == "date") {
      obj = {
        $formkit: "date",
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
      if (item.multiple) {
        if (item.multiple == false) {
          obj = {
            $formkit: "checkbox",
            multiple: true,
            options: item.options,
            ...obj,
          }
        } else {
          if (hasFormkitPro) {
            if (item.allow_new) {
              obj = {
                $formkit: "taglist",
                allowNewValues: true,
                options: item.options,
                ...obj,
              }
            } else {
              obj = {
                $formkit: "dropdown",
                multiple: true,
                options: item.options,
                "selection-appearance": "tags",
                ...obj,
              }
            }
          } else {
            obj = {
              $formkit: "checkbox",
              multiple: true,
              options: item.options,
              ...obj,
              help: "Select all that apply by holding command (macOS) or control (PC).",
            }
          }
        }
        output_schema.push(obj)
      } else {
        if (hasFormkitPro) {
          obj = {
            $formkit: "dropdown",
            options: item.options,
            "selection-removable": true,
            ...obj,
          }
        } else {
          obj = {
            $formkit: "checkbox",
            options: item.options,
            validation: "max:1",
            ...obj,
          }
        }
        output_schema.push(obj)
      }
    }
  }
  return output_schema
}

function createPayload(selected) {
  const payload = {}
  const validKeys = [
    "id",
    "form_data",
    "attorney_form_data",
    "status",
    "attorney_status",
    "attorney_questions",
    "attorney_analysis",
    "incident_id",
    "form_type_id",
  ]
  Object.keys(selected).forEach((key) => {
    if (validKeys.includes(key)) payload[key] = selected[key]
  })
  payload["form_data"] = JSON.stringify(payload["form_data"])
  payload["attorney_form_data"] = JSON.stringify(payload["attorney_form_data"])
  payload["project_id"] = selected.project.id
  return payload
}

function save({ commit, dispatch }) {
  commit("SET_SELECTED_LOADING", true)
  if (!state.selected.id) {
    return FormsApi.create(createPayload(state.selected))
      .then((response) => {
        commit("SET_DIALOG_CREATE_EDIT", false)
        commit("SET_DIALOG_ATTORNEY_EDIT", false)
        dispatch("getAll")
        commit("SET_SELECTED_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Form type created successfully.", type: "success" },
          { root: true }
        )
        if (state.selected.status == "Completed") {
          FormsApi.sendEmailToService(response.data.id)
        }
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
      .then((response) => {
        commit("SET_DIALOG_CREATE_EDIT", false)
        commit("SET_DIALOG_ATTORNEY_EDIT", false)
        dispatch("getAll")
        dispatch("forms_table/getAll", null, { root: true })
        commit("SET_SELECTED_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Form updated successfully.", type: "success" },
          { root: true }
        )
        if (state.selected.status == "Completed") {
          FormsApi.sendEmailToService(response.data.id)
        }
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
        commit("SET_ATTORNEY_PAGE_SCHEMA", getCurrentPage(response.data.attorney_form_schema))
        commit("SET_FORM_TYPE", response.data)
        commit("SET_DIALOG_CREATE_EDIT", true)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  },
  editShow({ commit }, selected) {
    commit("SET_SELECTED", selected)
    commit("SET_PAGE_SCHEMA", getCurrentPage(selected.form_type.form_schema))
    commit("SET_ATTORNEY_PAGE_SCHEMA", getCurrentPage(selected.form_type.attorney_form_schema))
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  attorneyEditShow({ commit }, selected) {
    commit("SET_SELECTED", selected)
    commit("SET_ATTORNEY_PAGE_SCHEMA", getCurrentPage(selected.form_type.attorney_form_schema))
    commit(
      "SET_PAGE_DATA",
      buildFormDoc(
        selected.form_type.form_schema,
        selected.form_data,
        selected.form_type.attorney_form_schema
      )
    )
    IncidentApi.get(selected.incident.id).then((response) => {
      commit("SET_INCIDENT_DATA", buildIncidentDoc(response.data))
      commit("SET_DIALOG_ATTORNEY_EDIT", true)
    })
  },
  attorneyEditShowById({ commit }, form_id) {
    commit("SET_TABLE_LOADING", true)
    FormsApi.get(form_id)
      .then((response) => {
        let selected = response.data
        commit("SET_TABLE_LOADING", false)
        commit("SET_SELECTED", selected)
        commit(
          "SET_PAGE_DATA",
          buildFormDoc(
            selected.form_type.form_schema,
            selected.form_data,
            selected.form_type.attorney_form_schema
          )
        )
        IncidentApi.get(selected.incident.id).then((response) => {
          commit("SET_INCIDENT_DATA", buildIncidentDoc(response.data))
          commit("SET_DIALOG_ATTORNEY_EDIT", true)
        })
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "Form id not found.", type: "exception" },
          { root: true }
        )
      })
  },
  showDeleteDialog({ commit }, form) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", form)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeAttorneyEdit({ commit }) {
    commit("SET_DIALOG_ATTORNEY_EDIT", false)
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
  saveAttorneyAnalysis({ commit, dispatch }) {
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
    state.selected.attorney_form_data = JSON.parse(state.selected.attorney_form_data)
  },
  SET_FORM_SCHEMA(state, value) {
    state.selected.form_schema = value
  },
  SET_ATTORNEY_PAGE_SCHEMA(state, value) {
    state.attorney_page_schema = value
  },
  SET_PAGE_SCHEMA(state, value) {
    state.page_schema = value
    state.has_formkit_pro = hasFormkitPro
  },
  SET_PAGE_DATA(state, value) {
    state.page_data = value
  },
  SET_INCIDENT_DATA(state, value) {
    state.incident_data = value
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
  SET_DIALOG_ATTORNEY_EDIT(state, value) {
    state.dialogs.showAttorneyEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showDeleteDialog = value
  },
  RESET_SELECTED(state) {
    // do not reset project
    let project = state.selected.project
    state.selected = { ...getDefaultSelectedState() }
    state.selected.project = project
    state.incident_id = null
    state.project_id = null
    state.page_schema = null
    state.attorney_page_schema = null
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
