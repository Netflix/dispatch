import API from "@/api"

const resource = "/individuals"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(termId) {
    return API.get(`${resource}/${termId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(termId, payload) {
    return API.put(`${resource}/${termId}`, payload)
  },

  delete(termId) {
    return API.delete(`${resource}/${termId}`)
  }
}
