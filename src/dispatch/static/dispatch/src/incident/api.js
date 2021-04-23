import API from "@/api"

const resource = "incidents"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(incidentId) {
    return API.get(`/${resource}/${incidentId}`)
  },

  getMetricForecast(options) {
    return API.get(`/${resource}/metric/forecast`, {
      params: { ...options },
    })
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },

  update(incidentId, payload) {
    return API.put(`/${resource}/${incidentId}`, payload)
  },

  createReport(incidentId, type, payload) {
    return API.post(`/${resource}/${incidentId}/report/${type}`, payload)
  },

  bulkUpdate(incidents, payload) {
    return Promise.all(
      incidents.map((incident) => {
        return this.update(incident.id, { ...incident, ...payload })
      })
    )
  },

  bulkDelete(incidents) {
    return Promise.all(
      incidents.map((incident) => {
        return this.delete(incident.id)
      })
    )
  },

  join(incidentId, payload) {
    return API.post(`/${resource}/${incidentId}/join`, payload)
  },

  delete(incidentId) {
    return API.delete(`/${resource}/${incidentId}`)
  },
}
