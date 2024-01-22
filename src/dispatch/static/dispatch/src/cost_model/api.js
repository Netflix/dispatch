import API from "@/api"

const resource = "cost_models"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },
  update(costModelId, payload) {
    return API.put(`/${resource}/${costModelId}`, payload)
  },
  delete(costModelId) {
    return API.delete(`/${resource}/${costModelId}`)
  },
}
