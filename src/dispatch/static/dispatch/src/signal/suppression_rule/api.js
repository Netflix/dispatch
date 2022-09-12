import API from "@/api"

const resource = "/signals/suppression/rules"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(suppressionRuleId) {
    return API.get(`${resource}/${suppressionRuleId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(suppressionRuleId, payload) {
    return API.put(`${resource}/${suppressionRuleId}`, payload)
  },

  delete(suppressionRuleId) {
    return API.delete(`${resource}/${suppressionRuleId}`)
  },
}
