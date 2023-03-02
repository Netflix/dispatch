import API from "@/api"

const resource = "/signals"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(signalId) {
    return API.get(`${resource}/${signalId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(signalId, payload) {
    return API.put(`${resource}/${signalId}`, payload)
  },

  delete(signalId) {
    return API.delete(`${resource}/${signalId}`)
  },

  getAllFilters(options) {
    return API.get(`${resource}/filters`, {
      params: { ...options },
    })
  },

  getAllInstances(options) {
    return API.get(`${resource}/instances`, {
      params: { ...options },
    })
  },

  getInstances(signalId) {
    return API.get(`${resource}/${signalId}/instances`)
  },

  getInstance(signalId, instanceId) {
    return API.get(`${resource}/${signalId}/${instanceId}`)
  },
}
