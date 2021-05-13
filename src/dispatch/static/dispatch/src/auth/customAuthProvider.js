import MeechumUser from "meechum-user-lib-js"

import store from "@/store"

function sessionTimeoutCallback() {
  store.commit(
    "app/SET_REFRESH",
    { show: true, message: "Your credentials have expired. Please refresh the page." },
    { root: true }
  )
}

function errorCallback() {
  store.commit(
    "app/SET_REFRESH",
    { show: true, message: "Your credentials have expired. Please refresh the page." },
    { root: true }
  )
}

function login(to, from, next) {
  // meechum auth stuff...
  MeechumUser.initialize("/meechum", 60, sessionTimeoutCallback, errorCallback).then(function () {
    let token = MeechumUser.getAccessToken()
    store.commit("auth/SET_USER_LOGIN", token)
    next()
  })
}

function logout(next) {
  next()
}

export default {
  login,
  logout,
}
