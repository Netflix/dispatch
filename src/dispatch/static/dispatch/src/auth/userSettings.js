import store from "@/store"
import UserApi from "./api"

function load() {
  if (!store.state.route.params.organization) {
    store.state.route.params.organization = "default"
  }

  return UserApi.getUserInfo().then(function (response) {
    return store.commit("auth/SET_USER_PROJECTS", response.data.projects)
  })
}

export default {
  load,
}
