import RouteApi from "@/route/api"

import { getField, updateField } from "vuex-map-fields"

const getDefaultRouteState = () => {
  return {
    text: null,
    context: {
      incident_priorities: [],
      incident_types: []
    }
  }
}

const getDefaultRecommendationState = () => {
  return {
    matched_terms: [],
    service_contacts: [],
    team_contacts: [],
    individual_contacts: [],
    documents: [],
    loading: false
  }
}

const state = {
  route: {
    ...getDefaultRouteState()
  },
  recommendation: {
    ...getDefaultRecommendationState()
  }
}

const getters = {
  getField
}

const actions = {
  getRecommendation({ commit, state }) {
    commit("SET_LOADING", true)
    return RouteApi.search(state.route)
      .then(response => {
        commit("SET_LOADING", false)
        commit("SET_RECOMMENDATION", response.data.recommendation)
      })
      .catch(() => {
        commit("SET_LOADING", false)
      })
  }
}

const mutations = {
  updateField,
  SET_LOADING(state, value) {
    state.recommendation.loading = value
  },
  SET_RECOMMENDATION(state, recommendation) {
    state.recommendation = recommendation
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
