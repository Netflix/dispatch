import API from "@/api"

const resource = "/incident_types"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(incidentTypeId) {
    return API.get(`${resource}/${incidentTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(incidentTypeId, payload) {
    return API.put(`${resource}/${incidentTypeId}`, payload)
  },

  delete(incidentTypeId) {
    return API.delete(`${resource}/${incidentTypeId}`)
  },
}
