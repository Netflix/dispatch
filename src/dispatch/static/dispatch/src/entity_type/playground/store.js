const state = {
  pattern: "",
}

const getters = {
  pattern({ pattern }) {
    return pattern
  },
}

const mutations = {
  updatePattern(state, payload) {
    state.pattern = payload
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
}
