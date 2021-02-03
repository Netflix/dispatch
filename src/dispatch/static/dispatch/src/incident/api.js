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

  createReport(incidentId, type, payload) {
    return API.post(`${resource}/${incidentId}/report/${type}`, payload)
  },

  bulkUpdate(incidents, payload) {
    return Promise.all(
      incidents.map(incident => {
        return this.update(incident.id, { ...incident, ...payload })
      })
    )
  },

  join(incidentId, payload) {
    return API.post(`${resource}/${incidentId}/join`, payload)
  },

  delete(incidentId) {
    return API.delete(`${resource}/${incidentId}`)
  }
}
