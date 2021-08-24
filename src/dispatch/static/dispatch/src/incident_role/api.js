import API from "@/api"

const resource = "/incident_roles"

export default {
  getRolePolicies(role, project_name) {
    return API.get(`${resource}/${role}`, { params: { project_name: project_name } })
  },

  updateRole(role, project_name, payload) {
    return API.put(`${resource}/${role}`, { params: { project_name: project_name }, data: payload })
  },
}
