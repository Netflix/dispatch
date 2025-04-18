import API from "@/api"
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import SearchUtils from "@/search/utils"

const resource = "cases"

export const caseKeys = {
  all: ['cases'],
  lists: () => [...caseKeys.all, 'list'],
  list: (filters) => [...caseKeys.lists(), { ...filters }],
  details: () => [...caseKeys.all, 'detail'],
  detail: (id) => [...caseKeys.details(), id],
}

const api = {
  getAll(options) {
    return API.get(`/${resource}`, {
      params: { ...options },
    })
  },

  get(caseId) {
    return API.get(`/${resource}/${caseId}`)
  },

  getParticipants(caseId, minimal = true) {
    return API.get(`/${resource}/${caseId}/participants`, {
      params: { minimal },
    })
  },

  create(payload) {
    return API.post(`/${resource}`, payload)
  },

  update(caseId, payload) {
    return API.put(`/${resource}/${caseId}`, payload)
  },

  escalate(caseId, payload) {
    return API.put(`/${resource}/${caseId}/escalate`, payload)
  },

  bulkUpdate(cases, payload) {
    return Promise.all(
      cases.map((case_obj) => {
        return this.update(case_obj.id, { ...case_obj, ...payload })
      })
    )
  },

  bulkDelete(cases) {
    return Promise.all(
      cases.map((case_obj) => {
        return this.delete(case_obj.id)
      })
    )
  },

  delete(caseId) {
    return API.delete(`/${resource}/${caseId}`)
  },

  join(caseId, payload) {
    return API.post(`/${resource}/${caseId}/join`, payload)
  },

  createAllResources(caseId, payload) {
    return API.post(`/${resource}/${caseId}/resources`, payload)
  },

  createCaseChannel(caseId, payload) {
    return API.post(`/${resource}/${caseId}/resources/conversation`, payload)
  },
}

// Query hooks
export const useCases = (options = {}) => {
  return useQuery({
    queryKey: caseKeys.list(options),
    queryFn: () => {
      const params = SearchUtils.createParametersFromTableOptions({ ...options }, "Case")
      return api.getAll(params).then(response => response.data)
    },
  })
}

export const useCase = (caseId) => {
  return useQuery({
    queryKey: caseKeys.detail(caseId),
    queryFn: () => api.get(caseId).then(response => response.data),
    enabled: !!caseId,
  })
}

export const useCaseByName = (caseName) => {
  return useQuery({
    queryKey: [...caseKeys.details(), 'byName', caseName],
    queryFn: () => {
      return api.getAll({
        filter: JSON.stringify([
          { and: [{ model: "Case", field: "name", op: "==", value: caseName }] },
        ]),
      }).then((response) => {
        if (response.data.items.length) {
          // get the full data set
          return api.get(response.data.items[0].id).then(response => response.data)
        }
        throw new Error(`Case '${caseName}' could not be found.`)
      })
    },
    enabled: !!caseName,
  })
}

// Mutation hooks
export const useCreateCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (caseData) => api.create(caseData).then(response => response.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

export const useUpdateCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ caseId, caseData }) => api.update(caseId, caseData).then(response => response.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
      queryClient.invalidateQueries({ queryKey: caseKeys.detail(data.id) })
    },
  })
}

export const useDeleteCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (caseId) => api.delete(caseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

export const useBulkUpdateCases = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ cases, payload }) => api.bulkUpdate(cases, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

export const useBulkDeleteCases = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (cases) => api.bulkDelete(cases),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

export const useJoinCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (caseId) => api.join(caseId, {}),
    onSuccess: (_, caseId) => {
      queryClient.invalidateQueries({ queryKey: caseKeys.detail(caseId) })
    },
  })
}

export const useEscalateCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ caseId, payload }) => api.escalate(caseId, payload).then(response => response.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

export default api
