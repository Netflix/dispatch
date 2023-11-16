import jwt_decode from "jwt-decode"
import router from "@/router/index"
import { differenceInMilliseconds, fromUnixTime, subMinutes } from "date-fns"
import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"
import UserApi from "./api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    email: null,
    loading: false,
    projects: null,
    role: null,
    password: null,
  }
}

const avatarTemplate = import.meta.env.VITE_DISPATCH_AVATAR_TEMPLATE

const state = {
  currentUser: {
    loggedIn: false,
    token: null,
    email: "",
    projects: [],
    role: null,
    experimental_features: false,
  },
  selected: {
    ...getDefaultSelectedState(),
  },
  loading: false,
  dialogs: {
    showCreateEdit: false,
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
      sortBy: ["email"],
      descending: [true],
    },
    loading: false,
  },
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    return UserApi.getAll(state.table.options).then((response) => {
      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", response.data)
    })
  }, 500),
  createEditShow({ commit }, plugin) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (plugin) {
      commit("SET_SELECTED", plugin)
    }
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return UserApi.create(state.selected).then(() => {
        dispatch("closeCreateEdit")
        dispatch("getAll")
        commit("SET_SELECTED_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "User created successfully.", type: "success" },
          { root: true }
        )
      })
    } else {
      return UserApi.update(state.selected.id, state.selected).then(() => {
        commit("SET_USER_PROJECTS", state.selected.projects)
        dispatch("closeCreateEdit")
        dispatch("getAll")
        commit("SET_SELECTED_LOADING", false)
        commit(
          "notification_backend/addBeNotification",
          { text: "User updated successfully.", type: "success" },
          { root: true }
        )
      })
    }
  },
  remove({ commit, dispatch }) {
    return UserApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "User deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
  loginRedirect({ state }, redirectUri) {
    let redirectUrl = new URL(redirectUri)
    void state
    let queryMap = {}
    for (var pair of redirectUrl.searchParams.entries()) {
      if (pair[0] in queryMap) {
        queryMap[pair[0]].push(pair[1])
      } else {
        queryMap[pair[0]] = [pair[1]]
      }
    }
    router.push({ path: redirectUrl.pathname, query: queryMap })
  },
  basicLogin({ commit }, payload) {
    commit("SET_BASIC_LOGIN_LOADING", true)
    UserApi.login(payload.email, payload.password).then(function (response) {
      commit("SET_USER_LOGIN", response.data.token)
      commit("SET_USER_PROJECTS", response.data.projects)
      router.push({
        name: "IncidentOverview",
      })
    })
    commit("SET_BASIC_LOGIN_LOADING", false)
  },
  register({ commit }, payload) {
    UserApi.register(payload.email, payload.password).then(function (response) {
      commit("SET_USER_LOGIN", response.data.token)
      router.push({
        name: "IncidentOverview",
      })
    })
  },
  login({ dispatch, commit }, payload) {
    commit("SET_USER_LOGIN", payload)
    dispatch("loginRedirect", payload.redirectUri).then(() => {
      dispatch("createExpirationCheck")
    })
  },
  logout({ commit }) {
    localStorage.removeItem("token")
    commit("SET_USER_LOGOUT")
    router.go()
  },
  getExperimentalFeatures({ commit }) {
    UserApi.getUserInfo()
      .then((response) => {
        commit("SET_EXPERIMENTAL_FEATURES", response.data.experimental_features)
      })
      .catch((error) => {
        console.error("Error occurred while updating experimental features: ", error)
      })
  },
  createExpirationCheck({ state, commit }) {
    // expiration time minus 10 min
    let expire_at = subMinutes(fromUnixTime(state.currentUser.exp), 10)
    let now = new Date()

    setTimeout(function () {
      commit(
        "app/SET_REFRESH",
        { show: true, message: "Your credentials have expired. Please refresh the page." },
        { root: true }
      )
    }, differenceInMilliseconds(expire_at, now))
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
  SET_BASIC_LOGIN_LOADING(state, value) {
    state.loading = value
  },
  SET_USER_LOGIN(state, token) {
    state.currentUser = {
      ...state.currentUser,
      ...jwt_decode(token),
      token: token,
      loggedIn: true,
    }
    localStorage.setItem("token", token)
  },
  SET_EXPERIMENTAL_FEATURES(state, value) {
    state.currentUser.experimental_features = value
  },
  SET_USER_LOGOUT(state) {
    state.currentUser = { loggedIn: false }
  },
  SET_USER_PROJECTS(state, value) {
    state.currentUser.projects = value
  },
}

const getters = {
  getField,
  userAvatarUrl: (state) => {
    if (!avatarTemplate) return ""
    const email = state.currentUser.email || ""
    const userId = email.split("@")[0]
    if (userId) {
      // to use avatar template, store in .env file and
      // put * as a placeholder for the userid
      const stem = avatarTemplate.replace("*", userId)
      const loc = `${window.location.protocol}//${window.location.host}${stem}`
      return loc
    }
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
