import API from "@/api"

const resource = "/forms"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(formId) {
    return API.get(`${resource}/${formId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(formId, creator_id, payload) {
    return API.put(`${resource}/${formId}/${creator_id}`, payload)
  },

  delete(formId, creator_id) {
    return API.delete(`${resource}/${formId}/${creator_id}`)
  },

  sendEmailToService(formId) {
    return API.post(`${resource}/completed/${formId}`)
  },
}
