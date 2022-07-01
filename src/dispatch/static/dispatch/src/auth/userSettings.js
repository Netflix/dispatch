import store from "@/store"
import UserApi from "./api"

function load() {
  UserApi.getUserInfo().then(function (response) {
    store.commit("auth/SET_USER_PROJECTS", response.data.projects)
  })
}

export default {
  load,
}
