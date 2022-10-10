import API from "@/api"

const resource = "signals"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(signalId) {
    return API.get(`/${resource}/${signalId}`)
  },

  getAllInstances(options) {
    return API.get(`/${resource}/instances`, {
      params: { ...options },
    })
  },

  getInstances(signalId) {
    return API.get(`/${resource}/${signalId}/instances`)
  },

  getInstance(signalId, instanceId) {
    return API.get(`/${resource}/${signalId}/${instanceId}`)
  },
}
