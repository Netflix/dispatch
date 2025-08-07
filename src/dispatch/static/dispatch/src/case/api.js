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
      cases.map(async (case_obj) => {
        try {
          // Fetch the full case data to ensure all required fields are available
          const fullCase = await this.get(case_obj.id)
          const updateResult = await this.update(case_obj.id, { ...fullCase.data, ...payload })
          return { caseId: case_obj.id, success: true, data: updateResult.data }
        } catch (error) {
          return { caseId: case_obj.id, success: false, error: error.message }
        }
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

  removeParticipant(caseId, email) {
    return API.delete(`/${resource}/${caseId}/remove/${email}`)
  },

  addParticipant(caseId, email) {
    return API.post(`/${resource}/${caseId}/add/${email}`)
  },

  createAllResources(caseId, payload) {
    return API.post(`/${resource}/${caseId}/resources`, payload)
  },

  createCaseChannel(caseId, payload) {
    return API.post(`/${resource}/${caseId}/resources/conversation`, payload)
  },

  createNewEvent(caseId, payload) {
    return API.post(`/${resource}/${caseId}/event`, payload)
  },

  updateEvent(caseId, payload) {
    return API.patch(`/${resource}/${caseId}/event`, payload)
  },

  deleteEvent(caseId, event_uuid) {
    return API.delete(`/${resource}/${caseId}/event/${event_uuid}`)
  },

  exportTimeline(caseId, timeline_filters) {
    return API.post(`/${resource}/${caseId}/exportTimeline`, timeline_filters)
  },
}
