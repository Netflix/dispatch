import API from "@/api"

const resource = "/teams"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(teamId) {
    return API.get(`${resource}/${teamId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(teamId, payload) {
    return API.put(`${resource}/${teamId}`, payload)
  },

  delete(teamId) {
    return API.delete(`${resource}/${teamId}`)
  },
}
