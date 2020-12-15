import TaskApi from "@/task/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce, forEach, each, has } from "lodash"

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
    source: null,
    id: null,
    loading: false
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState()
  },
  dialogs: {
    showCreateEdit: false,
    showRemove: false
  },
  table: {
    rows: {
      items: [],
      total: null,
      selected: []
    },
    options: {
      filters: {
        creator: [],
        owner: [],
        assignee: [],
        incident: [],
        incident_type: [],
        incident_priority: [],
        status: []
      },
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["status"],
      descending: [false]
    },
    loading: false,
    bulkEditLoading: false
  }
}

const getters = {
  getField
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let tableOptions = Object.assign({}, state.table.options)
    delete tableOptions.filters

    tableOptions.fields = []
    tableOptions.ops = []
    tableOptions.values = []

    forEach(state.table.options.filters, function(value, key) {
      each(value, function(value) {
        if (has(value, "id")) {
          tableOptions.fields.push(key + ".id")
          tableOptions.values.push(value.id)
        } else {
          tableOptions.fields.push(key)
          tableOptions.values.push(value)
        }
        tableOptions.ops.push("==")
      })
    })
    return TaskApi.getAll(tableOptions).then(response => {
      commit("SET_TABLE_LOADING", "primary")
      commit("SET_TABLE_ROWS", response.data)
    })
  }, 200),
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
  save({ commit, dispatch }) {
    if (!state.selected.id) {
      return TaskApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "app/SET_SNACKBAR",
            { text: "Task created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Task not created. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    } else {
      return TaskApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "app/SET_SNACKBAR",
            { text: "Task updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Task not updated. Reason: " + err.response.data.detail,
              type: "error"
            },
            { root: true }
          )
        })
    }
  },
  saveBulk({ commit, dispatch }, payload) {
    commit("SET_BULK_EDIT_LOADING", true)
    return TaskApi.bulkUpdate(state.table.rows.selected, payload)
      .then(() => {
        dispatch("getAll")
        commit(
          "app/SET_SNACKBAR",
          { text: "Task(s) updated successfully.", type: "success" },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
      .catch(err => {
        console.log(err)
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Task(s) not updated. Reason: " + err.response.data.detail,
            type: "error"
          },
          { root: true }
        )
        commit("SET_BULK_EDIT_LOADING", false)
      })
  },
  remove({ commit, dispatch }) {
    return TaskApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit(
          "app/SET_SNACKBAR",
          { text: "Task deleted successfully.", type: "success" },
          { root: true }
        )
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Task not deleted. Reason: " + err.response.data.detail,
            type: "error"
          },
          { root: true }
        )
      })
  }
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
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  SET_BULK_EDIT_LOADING(state, value) {
    state.table.bulkEditLoading = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
