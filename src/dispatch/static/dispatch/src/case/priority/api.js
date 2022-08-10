import API from "@/api"

const resource = "/case_priorities"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },
  get(casePriorityId) {
    return API.get(`${resource}/${casePriorityId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(casePriorityId, payload) {
    return API.put(`${resource}/${casePriorityId}`, payload)
  },

  delete(casePriorityId) {
    return API.delete(`${resource}/${casePriorityId}`)
  },
}
