import MeechumUser from "meechum-user-lib-js"

MeechumUser.initialize()

export function login(to, from, next) {
  // meechum auth stuff...
  next()
}
