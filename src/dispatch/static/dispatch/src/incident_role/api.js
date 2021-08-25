import API from "@/api"

const resource = "/incident_roles"

export default {
  getRolePolicies(role, project_name) {
    return API.get(`${resource}/${role}`, { params: { projectName: project_name } })
  },

  updateRole(role, project_name, payload) {
    return API.put(`${resource}/${role}`, payload, { params: { projectName: project_name } })
  },
}
