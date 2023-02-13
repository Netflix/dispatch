import API from "@/api"

const resource = "/entity"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(EntityId) {
    return API.get(`${resource}/${EntityId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(EntityId, payload) {
    return API.put(`${resource}/${EntityId}`, payload)
  },

  delete(EntityId) {
    return API.delete(`${resource}/${EntityId}`)
  },

  async getCasesCount(EntityId) {
    return await API.get(`${resource}/${EntityId}/cases`)
  },

  async getSignalInstances(EntityId) {
    return await API.get(`${resource}/${EntityId}/signal_instances`)
  },
}
