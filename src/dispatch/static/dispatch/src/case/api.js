import API from "@/api"

const resource = "cases"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(caseId) {
    return API.get(`/${resource}/${caseId}`)
  },

  getParticipants(caseId, minimal = true) {
    return API.get(`/${resource}/${caseId}/participants`, {
      params: { minimal },
    })
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },

  update(caseId, payload) {
    return API.put(`/${resource}/${caseId}`, payload)
  },

  escalate(caseId, payload) {
    return API.put(`/${resource}/${caseId}/escalate`, payload)
  },

  bulkUpdate(cases, payload) {
    return Promise.all(
      cases.map((case_obj) => {
        return this.update(case_obj.id, { ...case_obj, ...payload })
      })
    )
  },

  bulkDelete(cases) {
    return Promise.all(
      cases.map((case_obj) => {
        return this.delete(case_obj.id)
      })
    )
  },

  delete(caseId) {
    return API.delete(`/${resource}/${caseId}`)
  },

  join(caseId, payload) {
    return API.post(`/${resource}/${caseId}/join`, payload)
  },

  createAllResources(caseId, payload) {
    return API.post(`/${resource}/${caseId}/resources`, payload)
  },
}
