import API from "@/api"

const resource = "signals"

export default {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(signalId) {
    return API.get(`/${resource}/${signalId}`)
  },
}
