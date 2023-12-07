import API from "@/api"

const resource = "plugins"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  getAllInstances(options) {
    return API.get(`/${resource}/instances`, {
      params: { ...options },
    })
  },

  getInstance(instanceId) {
    return API.get(`/${resource}/instances/${instanceId}`)
  },

  createInstance(payload) {
    return API.post(`/${resource}/instances`, payload)
  },

  updateInstance(instanceId, payload) {
    return API.put(`/${resource}/instances/${instanceId}`, payload)
  },

  deleteInstance(instanceId) {
    return API.delete(`/${resource}/instances/${instanceId}`)
  },

  getAllPluginEvents(options) {
    return API.get(`/${resource}/plugin_events`, {
      params: { ...options },
    })
  },
}
