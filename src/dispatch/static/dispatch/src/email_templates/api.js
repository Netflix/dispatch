import API from "@/api"

const resource = "/email_template"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(emailTemplateId) {
    return API.get(`${resource}/${emailTemplateId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(emailTemplateId, payload) {
    return API.put(`${resource}/${emailTemplateId}`, payload)
  },

  delete(emailTemplateId) {
    return API.delete(`${resource}/${emailTemplateId}`)
  },
}
