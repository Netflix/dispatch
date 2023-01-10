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
  }
}

function authCurrentUser (base, token, bad_token_ok=false) {
  let decodedToken
  let loggedIn
  try {
    decodedToken = jwt_decode(token)
    loggedIn = true
  } catch (e) {
    if (!bad_token_ok) {
      throw e
    }
    token = null
    decodedToken = {}
    loggedIn = false
  }

  return {
    ...base,
    loggedIn: loggedIn,
    token: token,
    ...decodedToken
  }
}

const state = {
  currentUser: authCurrentUser({
    loggedIn: false,
    token: null,
    email: "",
    projects: [],
    role: null,
  }, localStorage.getItem("token"), true),
  selected: {
    ...getDefaultSelectedState(),
  },
  loading: false,
  dialogs: {
    showEdit: false,
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
  editShow({ commit }, plugin) {
    commit("SET_DIALOG_EDIT", true)
    if (plugin) {
      commit("SET_SELECTED", plugin)
    }
  },
  closeEdit({ commit }) {
    commit("SET_DIALOG_EDIT", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    if (!state.selected.id) {
      return UserApi.create(state.selected).then(() => {
        dispatch("closeEdit")
        dispatch("getAll")
        commit(
          "notification_backend/addBeNotification",
          { text: "User created successfully.", type: "success" },
          { root: true }
        )
      })
    } else {
      return UserApi.update(state.selected.id, state.selected).then(() => {
        commit("SET_USER_PROJECTS", state.selected.projects)
        dispatch("closeEdit")
        dispatch("getAll")
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
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    state.table.rows = value
  },
  SET_DIALOG_EDIT(state, value) {
    state.dialogs.showEdit = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_BASIC_LOGIN_LOADING(state, value) {
    state.loading = value
  },
  SET_USER_LOGIN(state, token) {
    state.currentUser = authCurrentUser(state.currentUser, token)
    localStorage.setItem("token", token)
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
  userAvatarURL: (state) => {
    if (state.currentUser.userId) {
      return `${window.location.protocol}//${window.location.host}/avatar/${state.currentUser.userId}/${state.currentUser.userId}.json`
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
