import API from "@/api"

const resource = "/definitions"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(definitionId) {
    return API.get(`${resource}/${definitionId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(definitionId, payload) {
    return API.put(`${resource}/${definitionId}`, payload)
  },

  delete(definitionId) {
    return API.delete(`${resource}/${definitionId}`)
  },
}
