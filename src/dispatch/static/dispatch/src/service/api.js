import API from "@/api"

const resource = "/services"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(serviceId) {
    return API.get(`${resource}/${serviceId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(serviceId, payload) {
    return API.put(`${resource}/${serviceId}`, payload)
  },

  delete(serviceId) {
    return API.delete(`${resource}/${serviceId}`)
  },
}
