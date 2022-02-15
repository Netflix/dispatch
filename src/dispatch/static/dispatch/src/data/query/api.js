import API from "@/api"

const resource = "/data/queries"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(queryId) {
    return API.get(`${resource}/${queryId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(queryId, payload) {
    return API.put(`${resource}/${queryId}`, payload)
  },

  delete(queryId) {
    return API.delete(`${resource}/${queryId}`)
  },
}
