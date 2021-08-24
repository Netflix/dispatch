import API from "@/api"

const resource = "/incident_roles"

export default {
  getRolePolicies(role, project_name) {
    return API.get(`${resource}/${role}`, { params: { projectName: project_name } })
  },

  updateRole(role, payload) {
    return API.put(`${resource}/${role}`, payload)
  },
}
