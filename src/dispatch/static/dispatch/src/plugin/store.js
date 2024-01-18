import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import PluginApi from "@/plugin/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    enabled: null,
    configuration: [],
    configuration_schema: {},
    formkit_configuration_schema: [],
    broken: false,
    project: null,
    plugin_instance: null,
    plugin: null,
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
      sortBy: ["Plugin.slug"],
      descending: [true],
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
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Plugin")
    return PluginApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  getAllInstances: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Plugin")
    return PluginApi.getAllInstances(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, plugin) {
    if (plugin && plugin.broken) {
      commit(
        "notification_backend/addBeNotification",
        {
          text: "Plugin not installed correctly. Please review the Dispatch logs or contact your Dispatch Administrator",
          type: "exception",
        },
        { root: true }
      )
      return
    }
    commit("SET_DIALOG_EDIT", true)
    if (plugin) {
      PluginApi.getInstance(plugin.id).then((response) => {
        commit("SET_SELECTED", response.data)
      })
    }
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_EDIT", false)
    commit("RESET_SELECTED")
  },
  removeShow({ commit }, plugin) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", plugin)
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return PluginApi.createInstance(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAllInstances")
          commit(
            "notification_backend/addBeNotification",
            { text: "Plugin instance created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return PluginApi.updateInstance(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAllInstances")
          commit(
            "notification_backend/addBeNotification",
            { text: "Plugin instance updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return PluginApi.deleteInstance(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAllInstances")
      commit(
        "notification_backend/addBeNotification",
        { text: "Plugin instance deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
}

function convertToFormkit(json_schema) {
  if (!json_schema.properties) {
    return []
  }
  var formkit_schema = []
  var title = {
    $el: "h1",
    children: json_schema.description,
  }
  formkit_schema.push(title)
  for (const [key, value] of Object.entries(json_schema.properties)) {
    var obj = {}
    if (value.type == "string" || value.type == "password") {
      obj = {
        $formkit: "text",
        name: key,
        label: value.title,
        help: value.description,
        validation: "required",
      }
    } else if (value.type == "boolean") {
      obj = {
        $cmp: "FormKit",
        props: {
          name: key,
          type: "checkbox",
          label: value.title,
          help: value.description,
        },
      }
    }
    formkit_schema.push(obj)
  }
  return formkit_schema
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    Object.keys(value).forEach(function (key) {
      if (value[key]) {
        state.selected[key] = value[key]
      }
    })
    state.selected.formkit_configuration_schema = convertToFormkit(value.configuration_schema)
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
  SET_DIALOG_EDIT(state, value) {
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
