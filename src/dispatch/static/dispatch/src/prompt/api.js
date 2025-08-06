import API from "@/api"

const resource = "/ai"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  getDefaults() {
    return API.get(`${resource}/defaults`)
  },

  get(promptId) {
    return API.get(`${resource}/${promptId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(promptId, payload) {
    return API.put(`${resource}/${promptId}`, payload)
  },

  delete(promptId) {
    return API.delete(`${resource}/${promptId}`)
  },
}
