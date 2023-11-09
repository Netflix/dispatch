import API from "@/api"

const resource = "/forms_type"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(formTypeId) {
    return API.get(`${resource}/${formTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(formTypeId, payload) {
    return API.put(`${resource}/${formTypeId}`, payload)
  },

  delete(formTypeId) {
    return API.delete(`${resource}/${formTypeId}`)
  },
}
