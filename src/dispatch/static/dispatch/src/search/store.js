import SearchApi from "@/search/api"
const state = {
  results: [],
  query: "",
  models: []
}

const getters = {}

const actions = {
  setQuery({ commit }, query) {
    commit("SET_QUERY", query)
  },
  setModels({ commit }, models) {
    commit("SET_MODELS", models)
  },
  getResults({ commit, state }) {
    return SearchApi.search(state.query, state.models).then(response => {
      commit("SET_RESULTS", response.data.results)
    })
  }
}

const mutations = {
  SET_RESULTS(state, results) {
    state.results = results
  },
  SET_QUERY(state, query) {
    state.query = query
  },
  SET_MODELS(state, models) {
    state.models = models
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
