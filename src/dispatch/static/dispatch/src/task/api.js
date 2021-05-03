import API from "@/api"

const resource = "/tasks"

export default {
  getAll(options) {
    return API.get(`${resource}`, { params: { ...options } })
  },

  get(taskId) {
    return API.get(`${resource}/${taskId}`)
  },

  create(payload) {
    return API.post(`${resource}`, payload)
  },

  update(taskId, payload) {
    return API.put(`${resource}/${taskId}`, payload)
  },

  bulkUpdate(tasks, payload) {
    return Promise.all(
      tasks.map((task) => {
        return this.update(task.id, { ...task, ...payload })
      })
    )
  },

  delete(taskId) {
    return API.delete(`${resource}/${taskId}`)
  },
}
