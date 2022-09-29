import API from "@/api"

const resource = "/workflows"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(workflowId) {
    return API.get(`${resource}/${workflowId}`)
  },

  getInstance(workflowInstanceId) {
    return API.get(`${resource}/instances/${workflowInstanceId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(workflowId, payload) {
    return API.put(`${resource}/${workflowId}`, payload)
  },

  run(workflowId, payload) {
    return API.post(`${resource}/${workflowId}/run`, payload)
  },

  delete(workflowId) {
    return API.delete(`${resource}/${workflowId}`)
  },
}
