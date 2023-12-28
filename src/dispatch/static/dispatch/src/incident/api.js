import API from "@/api"
//import { result } from "lodash"

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

  bulkUpdate(incidents, payload) {
    return Promise.all(
      incidents.map((incident) => {
        return this.update(incident.id, { ...incident, ...payload })
      })
    )
  },

  delete(incidentId) {
    return API.delete(`/${resource}/${incidentId}`)
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

  subscribe(incidentId, payload) {
    return API.post(`/${resource}/${incidentId}/subscribe`, payload)
  },

  createReport(incidentId, type, payload) {
    return API.post(`/${resource}/${incidentId}/report/${type}`, payload)
  },

  createNewEvent(incidentId, payload) {
    return API.post(`/${resource}/${incidentId}/event`, payload)
  },

  updateEvent(incidentId, payload) {
    return API.patch(`/${resource}/${incidentId}/event`, payload)
  },

  deleteEvent(incidentId, event_uuid) {
    return API.delete(`/${resource}/${incidentId}/event/${event_uuid}`)
  },

  createAllResources(incidentId, payload) {
    return API.post(`/${resource}/${incidentId}/resources`, payload)
  },
  exportTimeline(incidentId, timeline_filters) {
    return API.post(`/${resource}/${incidentId}/exportTimeline`, timeline_filters)
  },
}
