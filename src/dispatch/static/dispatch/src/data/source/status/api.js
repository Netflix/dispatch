import API from "@/api"

const resource = "/data/sources/statuses"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(statusId) {
    return API.get(`${resource}/${statusId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(statusId, payload) {
    return API.put(`${resource}/${statusId}`, payload)
  },

  delete(statusId) {
    return API.delete(`${resource}/${statusId}`)
  },
}
