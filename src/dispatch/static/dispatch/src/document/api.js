import API from "@/api"

const resource = "/documents"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(documentId) {
    return API.get(`${resource}/${documentId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(documentId, payload) {
    return API.put(`${resource}/${documentId}`, payload)
  },

  delete(documentId) {
    return API.delete(`${resource}/${documentId}`)
  },
}
