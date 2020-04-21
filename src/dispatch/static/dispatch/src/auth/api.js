import API from "@/api"

const resource = "/auth"

export default {
  getUserInfo() {
    return API.get(`${resource}/userinfo`)
  },
  login(email, password) {
    return API.post(`${resource}/login`, { email: email, password: password })
  },
  register(email, password) {
    return API.post(`${resource}/register`, { email: email, password: password })
  }
}
