import API from "@/api"

const resource = "/case_types"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(caseTypeId) {
    return API.get(`${resource}/${caseTypeId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(caseTypeId, payload) {
    return API.put(`${resource}/${caseTypeId}`, payload)
  },

  delete(caseTypeId) {
    return API.delete(`${resource}/${caseTypeId}`)
  },
}
