import API from "@/api"

const resource = "/incident_costs"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(incidentCostId) {
    return API.get(`${resource}/${incidentCostId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(incidentCostId, payload) {
    return API.put(`${resource}/${incidentCostId}`, payload)
  },

  delete(incidentCostId) {
    return API.delete(`${resource}/${incidentCostId}`)
  }
}
