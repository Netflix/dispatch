import { getField, updateField } from "vuex-map-fields"
import router from "@/router"

const getDefaultRefreshState = () => {
  return {
    show: false,
    message: "",
  }
}

const latest_commit_hash = import.meta.env.VITE_DISPATCH_COMMIT_MESSAGE
const latest_commit_message = import.meta.env.VITE_DISPATCH_COMMIT_MESSAGE

const state = {
  toggleDrawer: true,
  refresh: {
    ...getDefaultRefreshState(),
  },
  loading: false,
  current_version: latest_commit_hash,
}

const getters = {
  getField,
}

const actions = {
  toggleDrawer({ commit }, value) {
    commit("TOGGLE_DRAWER", value)
  },
  performRefresh({ commit }) {
    router.go()
    commit("RESET_REFRESH")
  },
  setLoading({ commit }, value) {
    commit("SET_LOADING", value)
  },
  showCommitMessage({ commit }) {
    commit(
      "notification_backend/addBeNotification",
      {
        text: `Hash: ${latest_commit_hash} | Message: ${latest_commit_message}`,
        type: "success",
      },
      { root: true }
    )
  },
}

const mutations = {
  updateField,
  TOGGLE_DRAWER(state) {
    state.toggleDrawer = !state.toggleDrawer
  },
  SET_REFRESH(state, value) {
    state.refresh = value
    state.refresh.show = true
  },
  SET_LOADING(state, value) {
    state.loading = value
  },
  RESET_REFRESH(state) {
    state.refresh = Object.assign(state.refresh, getDefaultRefreshState())
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
