import API from "@/api"

const resource = "/feedback"

export default {
  getAll(options) {
    return API.get(`${resource}/`, { params: { ...options } })
  },

  get(feedbackId) {
    return API.get(`${resource}/${feedbackId}`)
  },

  create(payload) {
    return API.post(`${resource}/`, payload)
  },

  update(feedbackId, payload) {
    return API.put(`${resource}/${feedbackId}`, payload)
  },

  delete(feedbackId) {
    return API.delete(`${resource}/${feedbackId}`)
  }
}
