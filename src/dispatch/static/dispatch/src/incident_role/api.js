import API from "@/api"

const resource = "/incident_roles"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(incidentRoleId) {
    return API.get(`${resource}/${incidentRoleId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(incidentRoleId, payload) {
    return API.put(`${resource}/${incidentRoleId}`, payload)
  },

  delete(incidentRoleId) {
    return API.delete(`${resource}/${incidentRoleId}`)
  },
}
