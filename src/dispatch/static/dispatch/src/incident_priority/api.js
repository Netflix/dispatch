import API from "@/api"

const resource = "/incident_priorities"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(incidentPriorityId) {
    return API.get(`${resource}/${incidentPriorityId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(incidentPriorityId, payload) {
    return API.put(`${resource}/${incidentPriorityId}`, payload)
  },

  delete(incidentPriorityId) {
    return API.delete(`${resource}/${incidentPriorityId}`)
  },
}
