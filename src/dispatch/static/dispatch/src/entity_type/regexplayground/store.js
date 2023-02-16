const state = {
  pattern: "",
  text: "",
  matches: "",
  flags: "g",
}

const getters = {
  flags({ flags }) {
    return flags
  },
  pattern({ pattern }) {
    return pattern
  },
  text({ text }) {
    return text
  },
  matches({ text, pattern, flags }) {
    return getMatches(text, pattern, flags)
  },
}

const mutations = {
  updatePattern(state, payload) {
    state.pattern = payload
  },
  updateText(state, payload) {
    state.text = payload
  },
  updateFlags(state, payload) {
    state.flags = payload
  },
}
