import API from "@/api"

const resource = "users"

export default {
  getAll(options) {
    return API.get(`/${resource}`, { params: { ...options } })
  },
  get(userId) {
    return API.get(`/${resource}/${userId}`)
  },
  update(userId, payload) {
    return API.put(`/${resource}/${userId}`, payload)
  },
  create(payload) {
    return API.post(`/${resource}`, payload)
  },
  getUserInfo() {
    return API.get(`/auth/me`)
  },
  getUserRole() {
    return API.get(`/auth/myrole`)
  },
  login(email, password) {
    return API.post(`/auth/login`, { email: email, password: password })
  },
  register(email, password) {
    return API.post(`/auth/register`, { email: email, password: password })
  },
}
