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
    console.log("**** create payload", JSON.stringify(payload))
    return API.post(`${resource}`, payload)
  },

  update(formId, creator_id, payload) {
    console.log("**** update payload", JSON.stringify(payload))
    return API.put(`${resource}/${formId}/${creator_id}`, payload)
  },

  delete(formId, creator_id) {
    return API.delete(`${resource}/${formId}/${creator_id}`)
  },
}
