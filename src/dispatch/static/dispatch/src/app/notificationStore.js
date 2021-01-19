import { getField, updateField } from "vuex-map-fields"

const state = {
  backendNotifications: []
}

const getters = {
  getField,
  getBackendNotifications({ state }) {
    return state.backendNotifications
  }
}

const mutations = {
  updateField,
  addBeNotification(state, payload) {
    if (payload.type === "error") {
      payload.timeout = 0
    }

    if (payload.show !== false) {
      payload.show = true
    }
    console.log(payload)
    state.backendNotifications.push({ ...payload })
  },
  removeBeNotification(state, index) {
    state.backendNotifications.splice(index, 1)
  },
  removeAllBeNotifications(state) {
    state.backendNotifications = []
  },
  setBeNotificationSeen(state, index) {
    state.backendNotifications[index].show = false
  }
}

const actions = {
  addBackendNotification({ commit }, payload) {
    commit("addBeNotification", payload)
  },
  removeBackendNotification({ commit }, payload) {
    commit("removeBeNotification", payload)
  },
  setBackendNotificationSeen({ commit }, payload) {
    commit("setBeNotificationSeen", payload)
  },
  removeAllBackendNotifications({ commit }) {
    commit("removeAllBeNotifications")
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
