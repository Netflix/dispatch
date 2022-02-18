import API from "@/api"

const resource = "/data/sources/dataFormats"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(dataFormatId) {
    return API.get(`${resource}/${dataFormatId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(dataFormatId, payload) {
    return API.put(`${resource}/${dataFormatId}`, payload)
  },

  delete(dataFormatId) {
    return API.delete(`${resource}/${dataFormatId}`)
  },
}
