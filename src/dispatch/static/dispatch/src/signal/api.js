import API from "@/api"

const resource = "/signals"

export default {
  getAll(options) {
    return API.get(`${resource}`, {
      params: { ...options },
    })
  },

  get(signalId) {
    return API.get(`${resource}/${signalId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(signalId, payload) {
    return API.put(`${resource}/update/${signalId}`, payload)
  },

  delete(signalId) {
    return API.delete(`${resource}/${signalId}`)
  },

  getAllFilters(options) {
    return API.get(`${resource}/filters`, {
      params: { ...options },
    })
  },

  getAllInstances(options) {
    return API.get(`${resource}/instances`, {
      params: { ...options },
    })
  },

  getInstances(signalId) {
    return API.get(`${resource}/${signalId}/instances`)
  },

  getInstance(signalId, instanceId) {
    return API.get(`${resource}/${signalId}/${instanceId}`)
  },

  getStats(entity_type_id, entity_value, num_days = null) {
    let days_filter
    if (num_days != null) {
      days_filter = `&num_days=${num_days}`
    } else {
      days_filter = ""
    }
    return API.get(
      `${resource}/stats?entity_type_id=${entity_type_id}&entity_value="${entity_value}"${days_filter}`
    )
  },
}
