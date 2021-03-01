import API from "@/api"

const resource = "/incident_cost_types"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(notificationId) {
    return API.get(`${resource}/${incidentCostTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(notificationId, payload) {
    return API.put(`${resource}/${incidentCostTypeId}`, payload)
  },

  delete(notificationId) {
    return API.delete(`${resource}/${incidentCostTypeId}`)
  }
}
