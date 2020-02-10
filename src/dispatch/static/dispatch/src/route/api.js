import API from "@/api"

const resource = "/route"

export default {
  search(payload) {
    return API.post(`${resource}/`, payload)
  }
}
