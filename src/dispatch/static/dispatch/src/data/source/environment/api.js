import API from "@/api"

const resource = "/data/sources/environments"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(environmentId) {
    return API.get(`${resource}/${environmentId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(environmentId, payload) {
    return API.put(`${resource}/${environmentId}`, payload)
  },

  delete(environmentId) {
    return API.delete(`${resource}/${environmentId}`)
  },
}
