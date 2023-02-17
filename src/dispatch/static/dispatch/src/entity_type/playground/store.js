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
    console.log("New pattern %O", payload)
    state.pattern = payload
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
}
