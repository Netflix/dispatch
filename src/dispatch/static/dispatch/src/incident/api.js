import API from "@/api"

const resource = "/incidents"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(incidentId) {
    return API.get(`${resource}/${incidentId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(incidentId, payload) {
    return API.put(`${resource}/${incidentId}`, payload)
  },

  // TODO: Still not clear to me we'll actually use delete() here, and like
  // this, for incidents.
  delete(incidentId) {
    return API.delete(`${resource}/${incidentId}`)
  }
}
