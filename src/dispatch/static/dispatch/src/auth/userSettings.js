import store from "@/store"
import UserApi from "./api"

function load() {
  UserApi.getUserInfo().then(function (response) {
    console.log("Loading user settings...")
    console.log(response.data.projects)
    store.commit("SET_USER_PROJECTS", response.data.projects)
  })
}

export default {
  load,
}
