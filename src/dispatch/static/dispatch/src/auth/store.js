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
    role: null,
    loading: false
  }
}

const state = {
  status: { loggedIn: false },
  userInfo: { email: "" },
  accessToken: localStorage.getItem("token") || null,
  selected: {
    ...getDefaultSelectedState()
  },
  loading: false,
  dialogs: {
    showEdit: false
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
      sortBy: ["email"],
      descending: [true]
    },
    loading: false
  }
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", true)
    return UserApi.getAll(state.table.options).then(response => {
      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", response.data)
    })
  }, 200),
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
      return UserApi.create(state.selected)
        .then(() => {
          dispatch("closeEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "User created successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "User not created. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    } else {
      return UserApi.update(state.selected.id, state.selected)
        .then(() => {
          dispatch("closeEdit")
          dispatch("getAll")
          commit("app/SET_SNACKBAR", { text: "User updated successfully." }, { root: true })
        })
        .catch(err => {
          commit(
            "app/SET_SNACKBAR",
            {
              text: "User not updated. Reason: " + err.response.data.detail,
              color: "red"
            },
            { root: true }
          )
        })
    }
  },
  remove({ commit, dispatch }) {
    return UserApi.delete(state.selected.id)
      .then(function() {
        dispatch("closeRemove")
        dispatch("getAll")
        commit("app/SET_SNACKBAR", { text: "User deleted successfully." }, { root: true })
      })
      .catch(err => {
        commit(
          "app/SET_SNACKBAR",
          {
            text: "User not deleted. Reason: " + err.response.data.detail,
            color: "red"
          },
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
    UserApi.login(payload.email, payload.password)
      .then(function(res) {
        commit("SET_USER_LOGIN", res.data.token)
        router.push({ path: "/dashboard" })
      })
      .catch(err => {
        commit("app/SET_SNACKBAR", { text: err.response.data.detail, color: "red" }, { root: true })
      })
    commit("SET_BASIC_LOGIN_LOADING", false)
  },
  register({ dispatch, commit }, payload) {
    UserApi.register(payload.email, payload.password)
      .then(function() {
        dispatch("basicLogin", payload)
      })
      .catch(err => {
        commit("app/SET_SNACKBAR", { text: err.response.data.detail, color: "red" }, { root: true })
      })
  },
  login({ dispatch, commit }, payload) {
    commit("SET_USER_LOGIN", payload.token)
    dispatch("loginRedirect", payload.redirectUri).then(() => {
      dispatch("createExpirationCheck")
    })
  },
  logout({ commit }) {
    commit("SET_USER_LOGOUT")
  },
  createExpirationCheck({ state, commit }) {
    // expiration time minus 10 min
    let expire_at = subMinutes(fromUnixTime(state.userInfo.exp), 10)
    let now = new Date()

    setTimeout(function() {
      commit(
        "app/SET_REFRESH",
        { show: true, message: "Your credentials have expired. Please refresh the page." },
        { root: true }
      )
    }, differenceInMilliseconds(expire_at, now))
  },
  getUserInfo({ commit }) {
    UserApi.getUserInfo().then(function(res) {
      commit("SET_USER_INFO", res.data)
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
  SET_DIALOG_EDIT(state, value) {
    state.dialogs.showEdit = value
  },
  RESET_SELECTED(state) {
    state.selected = Object.assign(state.selected, getDefaultSelectedState())
  },
  SET_USER_INFO(state, info) {
    state.userInfo = info
  },
  SET_BASIC_LOGIN_LOADING(state, value) {
    state.loading = value
  },
  SET_USER_LOGIN(state, accessToken) {
    state.accessToken = accessToken
    state.status = { loggedIn: true }
    state.userInfo = jwt_decode(accessToken)
    localStorage.setItem("token", accessToken)
  },
  SET_USER_LOGOUT(state) {
    state.status = { loggedIn: false }
    state.userInfo = null
    state.accessToken = null
    localStorage.removeItem("token")
  }
}

const getters = {
  getField,
  accessToken: () => state.accessToken,
  email: () => state.userInfo.email,
  exp: () => state.userInfo.exp
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
