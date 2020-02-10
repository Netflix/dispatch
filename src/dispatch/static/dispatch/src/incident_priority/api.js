import API from "@/api"

const resource = "/incident_priorities"

export default {
  getAll() {
    return API.get(`${resource}/`)
  }
}
