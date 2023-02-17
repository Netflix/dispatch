import API from "@/api"

const resource = "/signals/filters"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(signalFilterId) {
    return API.get(`${resource}/${signalFilterId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(signalFilterId, payload) {
    return API.put(`${resource}/${signalFilterId}`, payload)
  },

  delete(signalFilterId) {
    return API.delete(`${resource}/${signalFilterId}`)
  },
}
