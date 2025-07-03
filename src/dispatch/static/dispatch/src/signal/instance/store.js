import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import SignalApi from "@/signal/api"
import SignalFilterApi from "@/signal/filter/api"
import EntityApi from "@/entity/api"

const state = {
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
  entityTable: {
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
  instanceTableOptions(state) {
    return state.instanceTable.options
  },
  entityTableOptions(state) {
    return state.entityTable.options
  },
  snoozeTableOptions(state) {
    return state.snoozeTable.options
  },
}

const actions = {
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
    commit("SET_ENTITY_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions(
      {
        ...state.entityTable.options,
      },
      "Entity"
    )
    return EntityApi.getAll(params)
      .then(async (response) => {
        const fetchSignalStats = async (entity) => {
          try {
            return await SignalApi.getStats(entity.entity_type.id, entity.value)
          } catch (error) {
            console.error(`Error fetching signal stats for entity ${entity.name}:`, error)
            return null
          }
        }

        const statsPromises = response.data.items.map(fetchSignalStats)
        const statsResults = await Promise.all(statsPromises)

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

        commit("SET_ENTITY_TABLE_LOADING", false)
        commit("SET_ENTITY_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_ENTITY_TABLE_LOADING", false)
      })
  }, 500),
}

const mutations = {
  updateField,
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
  SET_ENTITY_TABLE_LOADING(state, value) {
    state.entityTable.loading = value
  },
  SET_ENTITY_TABLE_ROWS(state, value) {
    state.entityTable.rows = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
