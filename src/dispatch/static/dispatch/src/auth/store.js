import jwt_decode from "jwt-decode"
import router from "@/router/index"
import { differenceInMilliseconds, fromUnixTime, subMinutes } from "date-fns"
import { getField, updateField } from "vuex-map-fields"
import LoginApi from "./api"

const state = {
  status: { loggedIn: false },
  userInfo: { email: "" },
  accessToken: null,
  creds: { email: "", password: "" }
}

const actions = {
  loginRedirect({ state }, redirectUri) {
    let redirectUrl = new URL(redirectUri)
    void state
    router.push({ path: redirectUrl.pathname })
  },
  basicLogin({ commit }) {
    LoginApi.login(state.creds.email, state.creds.password)
      .then(function(res) {
        commit("SET_USER_LOGIN", res.data.token)
        router.push("/dashboard")
      })
      .catch(function() {
        commit("app/SET_SNACKBAR", { text: "Invalid credentials", color: "red" }, { root: true })
      })
  },
  register({ commit }) {
    LoginApi.register(state.creds.email, state.creds.password)
      .then(function(res) {
        commit("SET_USER_LOGIN", res.data.token)
        router.push("/dashboard")
      })
      .catch(function() {
        commit("app/SET_SNACKBAR", { text: "Invalid credentials", color: "red" }, { root: true })
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
  }
}

const mutations = {
  updateField,
  SET_USER_LOGIN(state, accessToken) {
    state.accessToken = accessToken
    state.status = { loggedIn: true }
    state.userInfo = jwt_decode(accessToken)
  },
  SET_USER_LOGOUT(state) {
    state.status = { loggedIn: false }
    state.userInfo = null
    state.accessToken = null
  }
}

const getters = {
  accessToken: () => state.accessToken,
  email: () => state.userInfo.email,
  exp: () => state.userInfo.exp,
  getField
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
