import jwt_decode from "jwt-decode"
import router from "@/router/index"
import { differenceInMilliseconds, fromUnixTime, subMinutes } from "date-fns"

const state = {
  status: { loggedIn: false },
  userInfo: { email: "" },
  accessToken: null
}

const actions = {
  loginRedirect({ state }, redirectUri) {
    let redirectUrl = new URL(redirectUri)
    router.push({ path: redirectUrl.pathname })
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
  accessToken: status => state.accessToken,
  email: status => state.userInfo.email,
  exp: status => state.userInfo.exp
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
