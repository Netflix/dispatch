import API from "@/api"

const resource = "/policies"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(policyId) {
    return API.get(`${resource}/${policyId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(policyId, payload) {
    return API.put(`${resource}/${policyId}`, payload)
  },

  delete(policyId) {
    return API.delete(`${resource}/${policyId}`)
  }
}
