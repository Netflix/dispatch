import API from "@/api"

const resource = "/auth"

export default {
  getUserInfo() {
    return API.get(`${resource}/userinfo`)
  }
}
