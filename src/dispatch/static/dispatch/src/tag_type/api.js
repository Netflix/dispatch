import API from "@/api"

const resource = "/tag_types"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(tagTypeId) {
    return API.get(`${resource}/${tagTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(tagTypeId, payload) {
    return API.put(`${resource}/${tagTypeId}`, payload)
  },

  delete(tagTypeId) {
    return API.delete(`${resource}/${tagTypeId}`)
  }
}
