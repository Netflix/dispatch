import API from "@/api"

const resource = "/data/sources/transports"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(transportId) {
    return API.get(`${resource}/${transportId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(transportId, payload) {
    return API.put(`${resource}/${transportId}`, payload)
  },

  delete(transportId) {
    return API.delete(`${resource}/${transportId}`)
  },
}
