import API from "@/api"

const resource = "/incident_cost_types"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(incidentCostTypeId) {
    return API.get(`${resource}/${incidentCostTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(incidentCostTypeId, payload) {
    return API.put(`${resource}/${incidentCostTypeId}`, payload)
  },

  delete(incidentCostTypeId) {
    return API.delete(`${resource}/${incidentCostTypeId}`)
  },
}
