import PolicyApi from "@/policy/api"
const state = {
  policies: [],
  selectedPolicy: {},
  filterOptions: {
    q: "",
    page: 1,
    itemsPerPage: 10,
    sortBy: "name",
    direction: "descending"
  },
  showDeleteDialog: false,
  showNewEditSheet: false,
  isLoading: false
}

const getters = {}

const actions = {
  setFilterOptions({ commit, dispatch }, value) {
    commit("SET_FILTER_OPTIONS", value)
    dispatch("getPolicies")
  },
  setLoading({ commit }, isLoading) {
    commit("SET_LOADING", isLoading)
  },
  showDeleteDialog({ commit }, value) {
    commit("SHOW_DELETE_DIALOG", value)

    if (!value) {
      commit("RESET_SELECTED_POLICY")
    }
  },
  showNewEditSheet({ commit }, value) {
    commit("SHOW_NEW_EDIT_SHEET", value)

    if (!value) {
      commit("RESET_SELECTED_POLICY")
    }
  },
  selectPolicy({ commit }, policy) {
    commit("SELECT_POLICY", policy)
  },
  resetSelectedPolicy({ commit }) {
    commit("RESET_SELECTED_POLICY")
  },
  updateSelectedPolicy({ commit }, value) {
    commit("UPDATE_SELECTED_POLICY", value)
  },
  addSelectedPolicyTerms({ commit }, terms) {
    commit("ADD_SELECTED_POLICY_TERMS", terms)
  },
  removeSelectedPolicyTerm({ commit }, term) {
    commit("REMOVE_SELECTED_POLICY_TERM", term)
  },
  getPolicies({ commit, state }) {
    commit("SET_LOADING", true)
    return PolicyApi.getAll(state.filterOptions).then(response => {
      commit("SET_LOADING", false)
      commit("SET_POLICIES", response.data)
    })
  },
  createPolicy({ commit }, policy) {
    return PolicyApi.create(policy).then(response => {
      commit("CREATE_POLICY", response.data)
      commit("SHOW_NEW_EDIT_SHEET", false)
      commit("RESET_SELECTED_POLICY")
    })
  },
  updatePolicy({ commit }, policy) {
    return PolicyApi.update(policy.id, policy).then(response => {
      commit("UPDATE_POLICY", response.data)
      commit("SHOW_NEW_EDIT_SHEET", false)
      commit("RESET_SELECTED_POLICY")
    })
  },
  deletePolicy({ commit }, policy) {
    return PolicyApi.delete(policy.id).then(response => {
      commit("DELETE_POLICY", response.data)
      commit("SHOW_DELETE_DIALOG", false)
      commit("RESET_SELECTED_POLICY")
    })
  }
}

const mutations = {
  SET_FILTER_OPTIONS(state, value) {
    state.filterOptions = Object.assign(state.filterOptions, value)
  },
  SET_LOADING(state, isLoading) {
    state.isLoading = isLoading
  },
  UPDATE_SELECTED_POLICY(state, value) {
    state.selectedPolicy = Object.assign(state.selectedPolicy, value)
  },
  ADD_SELECTED_POLICY_TERMS(state, terms) {
    state.selectedPolicy.terms = terms.map(function(t) {
      if (typeof t === "string") {
        return { text: t }
      }
      return t
    })
  },
  REMOVE_SELECTED_POLICY_TERM(state, term) {
    var termIndex = state.selectedPolicy.terms.indexOf(term)
    state.selectedPolicy.terms.pop(termIndex)
  },
  SHOW_DELETE_DIALOG(state, value) {
    state.showDeleteDialog = value
  },
  SHOW_NEW_EDIT_SHEET(state, value) {
    state.showNewEditSheet = value
  },
  SELECT_POLICY(state, policy) {
    state.selectedPolicy = policy
  },
  RESET_SELECTED_POLICY(state) {
    state.selectedPolicy = {
      name: null,
      description: null,
      expression: null
    }
  },
  SET_POLICIES(state, policies) {
    state.policies = policies
  },
  CREATE_POLICY(state, policy) {
    state.policies.items.push(policy)
  },
  UPDATE_POLICY(state, policy) {
    var policyIndex = state.policies.indexOf(policy)
    state.policies.items[policyIndex] = policy
  },
  DELETE_POLICY(state, policy) {
    var policyIndex = state.policies.indexOf(policy)
    state.policies.items.pop(policyIndex)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
