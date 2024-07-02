import API from "@/api"

const resource = "/case_cost_types"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(caseCostTypeId) {
    return API.get(`${resource}/${caseCostTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(caseCostTypeId, payload) {
    return API.put(`${resource}/${caseCostTypeId}`, payload)
  },

  delete(caseCostTypeId) {
    return API.delete(`${resource}/${caseCostTypeId}`)
  },
}
