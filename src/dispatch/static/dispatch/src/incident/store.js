import IncidentApi from "@/incident/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

const getDefaultSelectedState = () => {
  return {
    commander: null,
    conference: null,
    conversation: null,
    created_at: null,
    description: null,
    documents: null,
    id: null,
    incident_priority: null,
    incident_type: null,
    name: null,
    reported_at: null,
    reporter: null,
    stable_at: null,
    status: null,
    storage: null,
    ticket: null,
    title: null,
    visibility: null,
    terms: [],
    tags: [],
    participants: null,
    loading: false
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState()
  },
  dialogs: {
    showEditSheet: false,
    showNewSheet: false,
    showRemove: false
  },
  table: {
    rows: {
      items: [],
      total: null
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["reported_at"],
      descending: [true]
    },
    loading: false
  }
}

const getters = {
  getField
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", true)
    return IncidentApi.getAll(state.table.options).then(response => {
      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", response.data)
    })
  }, 200),
  get({ commit, state }) {
    return IncidentApi.get(state.selected.id).then(response => {
      commit("SET_SELECTED", response.data)
    })
  },
  showNewSheet({ commit }, incident) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", true)
    if (incident) {
      commit("SET_SELECTED", incident)
    }
  },
  closeNewSheet({ commit }) {
    commit("SET_DIALOG_SHOW_NEW_SHEET", false)
    commit("RESET_SELECTED")
  },
  showEditSheet({ commit }, incident) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", true)
    if (incident) {
      commit("SET_SELECTED", incident)
    }
  },
  closeEditSheet({ commit }) {
    commit("SET_DIALOG_SHOW_EDIT_SHEET", false)
    commit("RESET_SELECTED")
  },
  removeShow({ commit }, incident) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", incident)
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    if (!state.selected.id) {
      commit("SET_SELECTED_LOADING", true)
      return IncidentApi.create(state.selected)
        .then(response => {
          commit("SET_SELECTED", response.data)
          commit("SET_SELECTED_LOADING", false)
          this.interval = setInterval(function() {
            if (state.selected.id) {
              dispatch("get")
            }

            // TODO this is fragile but we don't set anything as "created"
            if (state.selected.conversation) {
              clearInterval(this.interval)
            }
          }, 5000)
        })
        .catch(() => {})
    } else {
      return IncidentApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "Incident updated successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Incident not updated. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return IncidentApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit("app/SET_SNACKBAR", { text: "Incident deleted successfully." }, { root: true })
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Incident not deleted. Reason: " + err.response.data.detail,
            color: "red"
          },
          { root: true }
        )
      })
  },
  resetSelected({ commit }) {
    commit("RESET_SELECTED")
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
    state.table.rows = value
  },
  SET_DIALOG_SHOW_EDIT_SHEET(state, value) {
    state.dialogs.showEditSheet = value
  },
  SET_DIALOG_SHOW_NEW_SHEET(state, value) {
    state.dialogs.showNewSheet = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
