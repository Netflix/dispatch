import API from "@/api"

const resource = "tags"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(tagId) {
    return API.get(`${resource}/${tagId}`)
  },

  getRecommendations(model, modelId) {
    return API.get(`/${resource}/recommendations/${model}/${modelId}`)
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },

  update(tagId, payload) {
    return API.put(`/${resource}/${tagId}`, payload)
  },

  delete(tagId) {
    return API.delete(`/${resource}/${tagId}`)
  },
}
