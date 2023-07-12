import API from "@/api"

const resource = "/signals/engagements"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(signalEngagementId) {
    return API.get(`${resource}/${signalEngagementId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(signalEngagementId, payload) {
    return API.put(`${resource}/${signalEngagementId}`, payload)
  },

  delete(signalEngagementId) {
    return API.delete(`${resource}/${signalEngagementId}`)
  },
}
