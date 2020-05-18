import store from "@/store"
export function login(to, from, next) {
  let token = localStorage.getItem("token")
  // we already have a token tell vuex about it
  if (token) {
    store.commit("auth/SET_USER_LOGIN", token)
    next()
  }

  // prevent redirect loop
  if (to.path !== "/login") {
    next("/login")
  }

  next()
}

export function logout(next) {
  next()
}
