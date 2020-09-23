import API from "@/api"

const resource = "/workflows"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(taskId) {
    return API.get(`${resource}/${workflowId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(workflowId, payload) {
    return API.put(`${resource}/${workflowId}`, payload)
  },

  delete(workflowId) {
    return API.delete(`${resource}/${workflowId}`)
  }
}
