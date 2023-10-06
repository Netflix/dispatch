import API from "@/api"

const resource = "/service_feedback"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  delete(feedbackId) {
    return API.delete(`${resource}/${feedbackId}`)
  },
}
