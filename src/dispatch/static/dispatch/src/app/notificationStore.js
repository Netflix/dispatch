import { getField, updateField } from "vuex-map-fields"

const state = {
  notifications: [],
}

const getters = {
  getField,
  getBackendNotifications({ state }) {
    return state.notifications
  },
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
    state.notifications.push({ ...payload })
  },
  removeBeNotification(state, index) {
    state.notifications.splice(index, 1)
  },
  removeAllBeNotifications(state) {
    state.notifications = []
  },
  setBeNotificationSeen(state, index) {
    state.notifications[index].show = false
  },
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
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
