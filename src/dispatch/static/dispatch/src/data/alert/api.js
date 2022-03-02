import API from "@/api"

const resource = "/data/alerts"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(alertId) {
    return API.get(`${resource}/${alertId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(alertId, payload) {
    return API.put(`${resource}/${alertId}`, payload)
  },

  delete(alertId) {
    return API.delete(`${resource}/${alertId}`)
  },
}
