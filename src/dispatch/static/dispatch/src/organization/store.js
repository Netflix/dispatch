import OrganizationApi from "@/organization/api"

import { getField, updateField } from "vuex-map-fields"
import router from "@/router/"

const getDefaultSelectedState = () => {
  return {
    name: null,
    description: [],
    banner_enabled: false,
    banner_text: null,
    banner_color: null,
    id: null,
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
  },
}

const getters = {
  getField,
}

const actions = {
  showCreateEditDialog({ commit }, organization) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (organization) {
      commit("SET_SELECTED", organization)
    }
  },
  closeCreateEditDialog({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    if (!state.selected.id) {
      return OrganizationApi.create(state.selected)
        .then(() => {
          dispatch("closeCreateEditDialog")
          router.go(router.currentRoute)
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Organization not created. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    } else {
      return OrganizationApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeCreateEditDialog")
          router.go(router.currentRoute)
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch((err) => {
          console.log(err)
          commit(
            "notification_backend/addBeNotification",
            {
              text: "Organization not updated. Reason: " + err.response.data.detail,
              type: "error",
            },
            { root: true }
          )
        })
    }
  },
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
