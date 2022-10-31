import API from "@/api"

const resource = "/signals/duplication/rules"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(duplicationRuleId) {
    return API.get(`${resource}/${duplicationRuleId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(duplicationRuleId, payload) {
    return API.put(`${resource}/${duplicationRuleId}`, payload)
  },

  delete(duplicationRuleId) {
    return API.delete(`${resource}/${duplicationRuleId}`)
  },
}
