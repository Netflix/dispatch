import API from "@/api"

const resource = "/data/sources"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(sourceId) {
    return API.get(`${resource}/${sourceId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(sourceId, payload) {
    return API.put(`${resource}/${sourceId}`, payload)
  },

  delete(sourceId) {
    return API.delete(`${resource}/${sourceId}`)
  },
}
