import store from "@/store"

function login(to, from, next) {
  let token = localStorage.getItem("token")

  if (token) {
    store.commit("auth/SET_USER_LOGIN", token)
    next()
  } else {
    // prevent redirect loop
    if (to.path !== "/auth/login") {
      next("/auth/login")
    } else {
      next()
    }
  }
}

function logout(next) {
  next()
}

export default {
  login,
  logout,
}
