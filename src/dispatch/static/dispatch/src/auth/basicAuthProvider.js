import store from "@/store"
export function login(to, from, next) {
  let token = localStorage.getItem("token")

  if (token) {
    store.commit("auth/SET_USER_LOGIN", token)
    next()
  } else {
    // prevent redirect loop
    if (to.path !== "/login") {
      next("/login")
    } else {
      next()
    }
  }
}

export function logout(next) {
  next()
}
