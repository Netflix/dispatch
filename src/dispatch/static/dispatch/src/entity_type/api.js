import API from "@/api"

const resource = "/entity_type"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(entityTypeId) {
    return API.get(`${resource}/${entityTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  create_with_case(payload, caseId) {
    return API.post(`${resource}/${caseId}`, payload)
  },

  update(entityTypeId, payload) {
    return API.put(`${resource}/${entityTypeId}`, payload)
  },

  process(entityTypeId, payload) {
    return API.put(`${resource}/${entityTypeId}/process`, payload)
  },

  delete(entityTypeId) {
    return API.delete(`${resource}/${entityTypeId}`)
  },

  recalculate(entityTypeId, caseId) {
    return API.put(`${resource}/recalculate/${entityTypeId}/${caseId}`)
  },
}
