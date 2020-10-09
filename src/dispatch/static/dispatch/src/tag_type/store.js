import TagTypeApi from "@/tag_type/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

const getDefaultSelectedState = () => {
  return {
    id: null,
    name: null,
    description: null,
    default: false
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
      total: null
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 10,
      sortBy: ["name"],
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
    return TagTypeApi.getAll(state.table.options)
      .then(response => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 200),
  createEditShow({ commit }, tagType) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (tagType) {
      commit("SET_SELECTED", tagType)
    }
  },
  removeShow({ commit }, tagType) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", tagType)
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
    if (!state.selected.id) {
      return TagTypeApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "Tag type created successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Tag type not created. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    } else {
      return TagTypeApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "Tag type updated successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "Tag type not updated. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return TagTypeApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit("app/SET_SNACKBAR", { text: "Tag type deleted successfully." }, { root: true })
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "Tag type not deleted. Reason: " + err.response.data.detail,
            color: "red"
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
    state.table.rows = value
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
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
