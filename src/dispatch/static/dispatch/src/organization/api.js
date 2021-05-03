import API from "@/api"

const resource = "/organizations"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(organizationId) {
    return API.get(`${resource}/${organizationId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(organizationId, payload) {
    return API.put(`${resource}/${organizationId}`, payload)
  },

  delete(organizationId) {
    return API.delete(`${resource}/${organizationId}`)
  },
}
