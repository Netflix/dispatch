import API from "@/api"

const resource = "/case_severities"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(caseSeverityId) {
    return API.get(`${resource}/${caseSeverityId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(caseSeverityId, payload) {
    return API.put(`${resource}/${caseSeverityId}`, payload)
  },

  delete(caseSeverityId) {
    return API.delete(`${resource}/${caseSeverityId}`)
  },
}
