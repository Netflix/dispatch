import store from "@/store"

function login(to, from, next) {
  let token = localStorage.getItem("token")

  if (token) {
    store.commit("auth/SET_USER_LOGIN", token)
    next()
  } else {
    // prevent redirect loop
    if (to.path !== "/default/auth/login") {
      next("/default/auth/login")
    } else {
      next()
    }
  }
}

export default {
  login,
}
