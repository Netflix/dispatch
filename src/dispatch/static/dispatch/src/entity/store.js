import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import EntityApi from "@/entity/api"
import SignalApi from "@/signal/api"
import API from "@/api"

const getDefaultSelectedState = () => {
  return {
    id: null,
    name: null,
    regular_expression: null,
    jpath: null,
    signal_instances: [],
    project: null,
    default: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCaseView: false,
    showCreateEdit: false,
    showRemove: false,
  },
  table: {
    rows: {
      items: [],
      total: null,
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["name"],
      descending: [true],
      filters: {
        project: [],
      },
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
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Entity")
    return EntityApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  // todo(amats): what's the difference between this and above?
  // todo(amats): can probably put back in signal directory store with new api hookups
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
  createEditShow({ commit }, entity) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (entity) {
      commit("SET_SELECTED", entity)
    }
  },
  createCaseShow({ commit }, cases) {
    commit("SET_DIALOG_CASE_VIEW", true)
    if (cases) {
      commit("SET_SELECTED", cases)
    }
  },
  closeCreateEditDialog({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  removeShow({ commit }, entity) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", entity)
  },
  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },
  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },
  save({ commit, state, dispatch }) {
    commit("SET_SELECTED_LOADING", true)
    if (!state.selected.id) {
      return EntityApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Entity created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return EntityApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Entity updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch, state }) {
    return EntityApi.delete(state.selected.id).then(() => {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Entity deleted successfully.", type: "success" },
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
  SET_SIGNAL_ENTITY_TABLE_LOADING(state, value) {
    state.signalEntityTable.loading = value
  },
  SET_SIGNAL_ENTITY_TABLE_ROWS(state, value) {
    state.signalEntityTable.rows = value
  },
  SET_DIALOG_CASE_VIEW(state, value) {
    state.dialogs.showCaseView = value
  },
  SET_DIALOG_CREATE_EDIT(state, value) {
    state.dialogs.showCreateEdit = value
  },
  SET_DIALOG_DELETE(state, value) {
    state.dialogs.showRemove = value
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
