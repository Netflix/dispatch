import API from "@/api"

const resource = "/incident_severities"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(incidentSeverityId) {
    return API.get(`${resource}/${incidentSeverityId}`)
  },
  create(payload) {
    return API.post(`${resource}`, payload)
  },
  update(incidentSeverityId, payload) {
    return API.put(`${resource}/${incidentSeverityId}`, payload)
  },
  delete(incidentSeverityId) {
    return API.delete(`${resource}/${incidentSeverityId}`)
  },
}
