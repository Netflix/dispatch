const state = {
  pattern: "",
  jpath: "",
}

const getters = {
  pattern({ pattern }) {
    return pattern
  },
  jpath({ jpath }) {
    return jpath
  },
}

const mutations = {
  updatePattern(state, payload) {
    state.pattern = payload
  },
  updateJsonPath(state, payload) {
    state.jpath = payload
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
}
