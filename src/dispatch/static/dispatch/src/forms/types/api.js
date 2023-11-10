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

  update(formTypeId, creator_id, payload) {
    return API.put(`${resource}/${formTypeId}/${creator_id}`, payload)
  },

  delete(formTypeId, creator_id) {
    return API.delete(`${resource}/${formTypeId}/${creator_id}`)
  },
}
