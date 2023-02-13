import API from "@/api"

const resource = "/entity"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(entityId) {
    return API.get(`${resource}/${entityId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(entityId, payload) {
    return API.put(`${resource}/${entityId}`, payload)
  },

  delete(entityId) {
    return API.delete(`${resource}/${entityId}`)
  },

  async getCasesCount(entityId) {
    return await API.get(`${resource}/${entityId}/cases`)
  },

  async getSignalInstances(entityId) {
    return await API.get(`${resource}/${entityId}/signal_instances`)
  },
}
