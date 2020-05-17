import API from "@/api"

const resource = "/incidents"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(incidentId) {
    return API.get(`${resource}/${incidentId}`)
  },

  getMetricForecast(incidentType) {
    return API.get(`${resource}/metric/forecast/${incidentType}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(incidentId, payload) {
    return API.put(`${resource}/${incidentId}`, payload)
  },

  join(incidentId, payload) {
    return API.post(`${resource}/${incidentId}/join`, payload)
  },

  // TODO: Still not clear to me we'll actually use delete() here, and like
  // this, for incidents.
  delete(incidentId) {
    return API.delete(`${resource}/${incidentId}`)
  }
}
