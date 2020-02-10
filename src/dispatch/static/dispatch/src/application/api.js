import API from "@/api"

const resource = "/applications"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(applicationId) {
    return API.get(`${resource}/${applicationId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(applicationId, payload) {
    return API.put(`${resource}/${applicationId}`, payload)
  },

  delete(applicationId) {
    return API.delete(`${resource}/${applicationId}`)
  }
}
