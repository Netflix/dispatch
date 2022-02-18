import API from "@/api"

const resource = "/data/sources/types"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(typeId) {
    return API.get(`${resource}/${typeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(typeId, payload) {
    return API.put(`${resource}/${typeId}`, payload)
  },

  delete(typeId) {
    return API.delete(`${resource}/${typeId}`)
  },
}
