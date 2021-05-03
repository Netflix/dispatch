import API from "@/api"

const resource = "/notifications"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(notificationId) {
    return API.get(`${resource}/${notificationId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(notificationId, payload) {
    return API.put(`${resource}/${notificationId}`, payload)
  },

  delete(notificationId) {
    return API.delete(`${resource}/${notificationId}`)
  },
}
