import API from "@/api"

const resource = "/user"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },
  get(userId) {
    return API.get(`${resource}/${userId}`)
  },
  update(userId, payload) {
    return API.put(`${resource}/${userId}`, payload)
  },
  getUserInfo() {
    return API.get(`${resource}/me`)
  },
  login(email, password) {
    return API.post(`/auth/login`, { email: email, password: password })
  },
  register(email, password) {
    return API.post(`$/auth/register`, { email: email, password: password })
  }
}
