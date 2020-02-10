import API from "@/api"

const resource = "/search/"

export default {
  search(query, models) {
    return API.get(`${resource}`, { params: { q: query, models: models } })
  }
}
