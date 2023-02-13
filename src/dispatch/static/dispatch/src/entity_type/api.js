import API from "@/api"

const resource = "/entity_type"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(EntityTypeId) {
    return API.get(`${resource}/${EntityTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(EntityTypeId, payload) {
    return API.put(`${resource}/${EntityTypeId}`, payload)
  },

  process(EntityTypeId, payload) {
    return API.put(`${resource}/${EntityTypeId}/process`, payload)
  },

  delete(EntityTypeId) {
    return API.delete(`${resource}/${EntityTypeId}`)
  },
}
