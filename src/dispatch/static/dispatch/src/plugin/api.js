import API from "@/api"

const resource = "/plugins"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(pluginId) {
    return API.get(`${resource}/${pluginId}`)
  },

  getByType(pluginType) {
    return API.get(`${resource}/${pluginType}`)
  },

  update(pluginId, payload) {
    return API.put(`${resource}/${pluginId}`, payload)
  }
}
