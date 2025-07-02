import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import SignalFilterApi from "@/signal/filter/api"
import EntityApi from "@/entity/api"
// todo(amats): not like this
import API from "@/api"

const getDefaultSelectedState = () => {
  return {
    case_priority: null,
    case_type: null,
    conversation_target: null,
    create_case: true,
    created_at: null,
    description: null,
    enabled: false,
    engagements: [],
    entity_types: [],
    external_id: null,
    external_url: null,
    filters: [],
    genai_enabled: false,
    genai_model: null,
    genai_prompt: null,
    genai_system_message: null,
    id: null,
    lifecycle: null,
    loading: false,
    name: null,
    oncall_service: null,
    owner: null,
    project: null,
    runbook: null,
    signal_definition: null,
    source: null,
    tags: [],
    variant: null,
    workflow_instances: null,
    workflows: [],
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showRawSignalDialog: false,
    showRemove: false,
    showHistory: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {
        case_priority: [],
        case_severity: [],
        case_type: [],
        project: [],
        tag: [],
        tag_type: [],
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["name"],
      descending: [true],
    },
    loading: false,
    bulkEditLoading: false,
  },
  instanceTable: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {
        created_at: {
          start: null,
          end: null,
        },
        signal: [],
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["created_at"],
      descending: [true],
    },
    loading: false,
  },
  signalEntityTable: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {
        created_at: {
          start: null,
          end: null,
        },
        // signal: [],
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["created_at"],
      descending: [true],
    },
    loading: false,
  },
  snoozeTable: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      filters: {
        created_at: {
          start: null,
          end: null,
        },
        action: ["snooze"], // exclude deduplications
      },
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["created_at"],
      descending: [true],
    },
    loading: false,
  },
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "signal")
    return SignalApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  getAllInstances: debounce(({ commit, state }) => {
    commit("SET_INSTANCE_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions(
      { ...state.instanceTable.options },
      "signal"
    )
    return SignalApi.getAllInstances(params)
      .then((response) => {
        commit("SET_INSTANCE_TABLE_LOADING", false)
        commit("SET_INSTANCE_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_INSTANCE_TABLE_LOADING", false)
      })
  }, 500),
  getAllSnoozes: debounce(({ commit, state }) => {
    commit("SET_SNOOZE_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.snoozeTable.options })
    return SignalFilterApi.getAll(params)
      .then((response) => {
        commit("SET_SNOOZE_TABLE_LOADING", false)
        commit("SET_SNOOZE_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_SNOOZE_TABLE_LOADING", false)
      })
  }, 500),
  getAllEntities: debounce(({ commit, state }) => {
    commit("SET_SIGNAL_ENTITY_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions(
      {
        ...state.signalEntityTable.options,
      },
      "Entity"
    )
    return EntityApi.getAll(params)
      .then(async (response) => {
        // Fetch signal stats for each entity in parallel
        const fetchSignalStats = async (entity) => {
          try {
            const url = `/signals/stats?entity_type_id=${entity.entity_type.id}&entity_value="${entity.value}"&num_days=1000`
            return await API.get(url)
          } catch (error) {
            console.error(`Error fetching signal stats for entity ${entity.name}:`, error)
            return null
          }
        }

        // Use Promise.all for parallel execution
        const statsPromises = response.data.items.map(fetchSignalStats)
        const statsResults = await Promise.all(statsPromises)

        // Append signal stats to each entity item so they can be accessed in the Vue file
        // todo(amats) can this be added to the async function for performance?
        statsResults.forEach((result, index) => {
          if (result) {
            const entity = response.data.items[index]
            // separate the stats to avoid duplicate column references when rendering
            let instanceStats = {
              num_signal_instances_alerted: result.data.num_signal_instances_alerted,
              num_signal_instances_snoozed: result.data.num_signal_instances_snoozed,
            }
            let snoozeStats = {
              num_snoozes_active: result.data.num_snoozes_active,
              num_snoozes_expired: result.data.num_snoozes_expired,
            }
            entity.instanceStats = instanceStats
            entity.snoozeStats = snoozeStats
          }
        })

        commit("SET_SIGNAL_ENTITY_TABLE_LOADING", false)
        commit("SET_SIGNAL_ENTITY_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_SIGNAL_ENTITY_TABLE_LOADING", false)
      })
  }, 500),
  get({ commit, state }) {
    return SignalApi.get(state.selected.id).then((response) => {
      commit("SET_SELECTED", response.data)
    })
  },
  createEditShow({ commit }, signal) {
    if (signal) {
      commit("SET_SELECTED", signal)
    }
    commit("SET_DIALOG_CREATE_EDIT", true)
  },
  showHistory({ commit }, signal) {
    if (signal) {
      commit("SET_SELECTED", signal)
    }
    commit("SET_DIALOG_HISTORY", true)
  },
  removeShow({ commit }, signal) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", signal)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  closeHistory({ commit }) {
    commit("SET_DIALOG_HISTORY", false)
    commit("RESET_SELECTED")
  },
  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return SignalApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal Definition created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return SignalApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Signal Definition updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return SignalApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Signal Definition deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
}

const mutations = {
  updateField,
  SET_SELECTED(state, value) {
    state.selected = Object.assign(state.selected, value)
  },
  SET_SELECTED_LOADING(state, value) {
    state.selected.loading = value
  },
  SET_TABLE_LOADING(state, value) {
    state.table.loading = value
  },
  SET_TABLE_ROWS(state, value) {
    state.table.rows = value
  },
  SET_INSTANCE_TABLE_LOADING(state, value) {
    state.instanceTable.loading = value
  },
  SET_INSTANCE_TABLE_ROWS(state, value) {
    state.instanceTable.rows = value
  },
  SET_SNOOZE_TABLE_LOADING(state, value) {
    state.snoozeTable.loading = value
  },
  SET_SNOOZE_TABLE_ROWS(state, value) {
    state.snoozeTable.rows = value
  },
  SET_SIGNAL_ENTITY_TABLE_LOADING(state, value) {
    state.signalEntityTable.loading = value
  },
  SET_SIGNAL_ENTITY_TABLE_ROWS(state, value) {
    state.signalEntityTable.rows = value
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
  },
  SET_DIALOG_HISTORY(state, value) {
    state.dialogs.showHistory = value
  },
  RESET_SELECTED(state) {
    // do not reset project
    let project = state.selected.project
    state.selected = { ...getDefaultSelectedState() }
    state.selected.project = project
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
