import { getField, updateField } from "vuex-map-fields"
import router from "@/router"

const getDefaultRefreshState = () => {
  return {
    show: false,
    message: "",
  }
}

const state = {
  toggleDrawer: true,
  refresh: {
    ...getDefaultRefreshState(),
  },
  loading: false,
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
