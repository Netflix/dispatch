import OrganizationApi from "@/organization/api"

import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"
import router from "@/router/"

const getDefaultSelectedState = () => {
  return {
    name: null,
    description: [],
    banner_enabled: false,
    banner_text: null,
    banner_color: "#1976D2FF",
    id: null,
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  selectedMember: {},
  dialogs: {
    showCreateEdit: false,
    showMemberEditDialog: false,
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
    return OrganizationApi.getAll(state.table.options)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
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
  showMemberEditDialog({ commit }, member) {
    commit("SET_SELECTED_MEMBER", member)
    commit("SET_DIALOG_MEMBER_EDIT", true)
  },
  closeMemberEditDialog({ commit }) {
    commit("RESET_SELECTED_MEMBER")
    commit("SET_DIALOG_MEMBER_EDIT", false)
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)

    if (!state.selected.id) {
      return OrganizationApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEditDialog")
          router.go(router.currentRoute)
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return OrganizationApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEditDialog")
          router.go(router.currentRoute)
          commit(
            "notification_backend/addBeNotification",
            { text: "Organization updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  updateMember({ commit }, payload) {
    return UserApi.update(payload.id, payload).then((response) => {
      commit("SET_DIALOG_MEMBER_EDIT", false)
      commit("auth/SET_USER_LOGIN", response.data.token)
      commit(
        "notification_backend/addBeNotification",
        { text: "User updated successfully.", type: "success" },
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
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_SELECTED_MEMBER(state, value) {
    state.selectedMember = Object.assign(state.selectedMember, value)
  },
  SET_DIALOG_MEMBER_EDIT(state, value) {
    state.dialogs.showMemberEditDialog = value
  },
  RESET_SELECTED_MEMBER(state) {
    state.selectedMember = Object.assign(state.selectedMember, getDefaultSelectedMemberState())
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
