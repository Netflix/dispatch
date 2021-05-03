import API from "@/api"

const resource = "projects"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(projectId) {
    return API.get(`/${resource}/${projectId}`)
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },

  update(projectId, payload) {
    return API.put(`/${resource}/${projectId}`, payload)
  },

  delete(projectId) {
    return API.delete(`/${resource}/${projectId}`)
  },
}
