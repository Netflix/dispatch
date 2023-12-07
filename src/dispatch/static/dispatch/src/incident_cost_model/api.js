import API from "@/api"

const resource = "/incident_cost_models"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },
  update(incidentCostModelId, payload) {
    return API.put(`/${resource}/${incidentCostModelId}`, payload)
  },
  delete(incidentCostModelId) {
    return API.delete(`/${resource}/${incidentCostModelId}`)
  },
}
