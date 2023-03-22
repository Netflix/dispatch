import API from "@/api"

const resource = "/workstream_types"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(workstreamId) {
    return API.get(`${resource}/${workstreamId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(workstreamId, payload) {
    return API.put(`${resource}/${workstreamId}`, payload)
  },

  delete(workstreamId) {
    return API.delete(`${resource}/${workstreamId}`)
  },
}
