import ProjectApi from "@/project/api"
import AuthApi from "@/auth/api"

/**
 * Resolves a project for a component based on various fallback strategies
 *
 * @param {Object} options - Configuration options
 * @param {Object} options.component - Vue component instance (for accessing this.project, this.default_project)
 * @param {Function} options.onProjectResolved - Callback when project is resolved
 * @param {Boolean} options.setDirectly - Whether to set component.project directly (default: true)
 * @returns {Promise} - Promise that resolves when project resolution is complete
 */
export const resolveProject = async ({ component, onProjectResolved, setDirectly = true }) => {
  // Check if project is already set
  if (component.project) {
    return component.project
  }

  // Try to get project from URL query parameters
  if (component.$route && component.$route.query.project) {
    const params = {
      filter: { field: "name", op: "==", value: component.$route.query.project },
    }

    try {
      const response = await ProjectApi.getAll(params)
      if (response.data.items.length) {
        const project = response.data.items[0]
        if (setDirectly) {
          component.project = project
        }
        if (onProjectResolved) {
          onProjectResolved(project)
        }
        return project
      }
    } catch (error) {
      console.error("Error fetching project from query params:", error)
    }
  }

  // Try to get project from user's projects
  if (component.projects && component.projects.length) {
    const project = component.projects[0].project
    if (setDirectly) {
      component.project = project
    }
    if (onProjectResolved) {
      onProjectResolved(project)
    }
    return project
  }

  // Try to get user's default project or organization default
  try {
    const response = await AuthApi.getUserInfo()

    // If project was set while waiting for API response, exit
    if (component.project) {
      return component.project
    }

    // Check for user's default project
    const defaultUserProject = response.data.projects.filter((v) => v.default === true)
    if (defaultUserProject.length) {
      const project = defaultUserProject[0].project
      if (setDirectly) {
        component.project = project
      }
      if (onProjectResolved) {
        onProjectResolved(project)
      }
      return project
    }

    // Try component's default_project
    if (component.default_project) {
      if (setDirectly) {
        component.project = component.default_project
      }
      if (onProjectResolved) {
        onProjectResolved(component.default_project)
      }
      return component.default_project
    }

    // Last resort: get organization default project
    const defaultParams = {
      filter: { field: "default", op: "==", value: true },
    }

    const projectResponse = await ProjectApi.getAll(defaultParams)
    if (projectResponse.data.items.length) {
      const project = projectResponse.data.items[0]
      if (setDirectly) {
        component.project = project
      }
      if (onProjectResolved) {
        onProjectResolved(project)
      }
      return project
    }
  } catch (error) {
    console.error("Error resolving project:", error)
  }

  return null
}
