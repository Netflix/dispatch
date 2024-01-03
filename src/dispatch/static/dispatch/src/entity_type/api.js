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

  update(entityTypeId, payload) {
    return API.put(`${resource}/${entityTypeId}`, payload)
  },

  process(entityTypeId, payload) {
    return API.put(`${resource}/${entityTypeId}/process`, payload)
  },

  delete(entityTypeId) {
    return API.delete(`${resource}/${entityTypeId}`)
  },

  recalculate(entityTypeId, signalInstanceId) {
    return API.put(`${resource}/recalculate/${entityTypeId}/${signalInstanceId}`)
  },
}
