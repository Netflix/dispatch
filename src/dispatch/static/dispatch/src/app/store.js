import { getField, updateField } from "vuex-map-fields"
import router from "@/router"

const getDefaultSnackbarState = () => {
  return {
    text: null,
    color: "primary",
    show: false,
    timeout: 2000
  }
}

const getDefaulRefreshState = () => {
  return {
    show: false,
    message: "blah"
  }
}

const state = {
  toggleDrawer: true,
  snackbar: {
    ...getDefaultSnackbarState()
  },
  refresh: {
    ...getDefaulRefreshState()
  },
  loading: false
}

const getters = {
  getField
}

const actions = {
  toggleDrawer({ commit }, value) {
    commit("TOGGLE_DRAWER", value)
  },
  closeSnackBar({ commit }) {
    commit("RESET_SNACKBAR")
  },
  performRefresh({ commit }) {
    router.go()
    commit("RESET_REFRESH")
  },
  setLoading({ commit }, value) {
    commit("SET_LOADING", value)
  }
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
  SET_SNACKBAR(state, value) {
    state.snackbar = value
    state.snackbar.show = true
  },
  SET_LOADING(state, value) {
    state.loading = value
  },
  RESET_SNACKBAR(state) {
    state.snackbar = Object.assign(state.snackbar, getDefaultSnackbarState())
  },
  RESET_REFRESH(state) {
    state.refresh = Object.assign(state.refresh, getDefaulRefreshState())
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
