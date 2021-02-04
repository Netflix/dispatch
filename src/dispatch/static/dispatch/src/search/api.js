import API from "@/api"

const resource = "/search"

export default {
  search(query, models) {
    return API.get(`${resource}`, { params: { q: query, models: models } })
  },
  getAllFilters(options) {
    return API.get(`${resource}/filters`, { params: { ...options } })
  },

  get(searchFilterId) {
    return API.get(`${resource}/filters/${searchFilterId}`)
  },

  create(payload) {
    return API.post(`${resource}/filters`, payload)
  },

  update(searchFilterId, payload) {
    return API.put(`${resource}/filters/${searchFilterId}`, payload)
  },

  delete(searchFilterId) {
    return API.delete(`${resource}/filters/${searchFilterId}`)
  },

  getByType(searchFilterType) {
    return API.get(`${resource}/filters/${searchFilterType}`)
  }
}
