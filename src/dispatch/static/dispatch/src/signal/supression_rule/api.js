import API from "@/api"

const resource = "/signals/supression/rules"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(supressionRuleId) {
    return API.get(`${resource}/${supressionRuleId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(supressionRuleId, payload) {
    return API.put(`${resource}/${supressionRuleId}`, payload)
  },

  delete(supressionRuleId) {
    return API.delete(`${resource}/${supressionRuleId}`)
  },
}
