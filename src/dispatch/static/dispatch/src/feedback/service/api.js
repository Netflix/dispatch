import API from "@/api"

const resource = "/service_feedback"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  delete(feedbackId, individualId) {
    return API.delete(`${resource}/${feedbackId}/${individualId}`)
  },
}
