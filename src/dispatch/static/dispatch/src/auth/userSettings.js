import store from "@/store"
import UserApi from "./api"

function load() {
  return UserApi.getUserInfo().then(function (response) {
    // Update the full current user data including settings
    store.commit("auth/SET_CURRENT_USER", response.data)
    // Also update projects for backward compatibility
    return store.commit("auth/SET_USER_PROJECTS", response.data.projects)
  })
}

export default {
  load,
}
