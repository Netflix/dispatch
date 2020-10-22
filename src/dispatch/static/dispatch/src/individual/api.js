import API from "@/api"

const resource = "/individuals"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(individualId) {
    return API.get(`${resource}/${individualId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(individualId, payload) {
    return API.put(`${resource}/${individualId}`, payload)
  },

  delete(individualId) {
    return API.delete(`${resource}/${individualId}`)
  }
}
