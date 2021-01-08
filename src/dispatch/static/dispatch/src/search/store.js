import SearchApi from "@/search/api"
const state = {
  results: [],
  query: "",
  models: [],
  loading: false
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
    commit("SET_LOADING", false)
    return SearchApi.search(state.query, state.models)
      .then(response => {
        commit("SET_RESULTS", response.data.results)
        commit("SET_LOADING", false)
      })
      .catch(err => {
        commit(
          "notification/addBeNotification",
          {
            text: "Search Failed. Reason: " + err.response.data.detail,
            color: "red"
          },
          { root: true }
        )
        commit("SET_LOADING", false)
      })
  }
}

const mutations = {
  SET_LOADING(state, value) {
    state.loading = value
  },
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
