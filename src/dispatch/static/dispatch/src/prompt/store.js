import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"
import PromptApi from "./api"

const getDefaultSelectedState = () => {
  return {
    genai_type: null,
    genai_prompt: null,
    genai_system_message: null,
    enabled: false,
    created_at: null,
    updated_at: null,
    project: null,
    id: null,
    loading: false,
  }
}

const state = {
  selected: {
    ...getDefaultSelectedState(),
  },
  dialogs: {
    showCreateEdit: false,
    showRemove: false,
  },
  table: {
    rows: {
      items: [],
      total: 0,
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["genai_type"],
      descending: [false],
      filters: {
        project: [],
      },
    },
    loading: false,
  },
  defaults: {
    prompts: {},
    system_messages: {},
    loading: false,
  },
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(async ({ commit, state, dispatch }) => {
    commit("SET_TABLE_LOADING", "primary")

    try {
      const params = {
        page: state.table.options.page,
        itemsPerPage: state.table.options.itemsPerPage,
        q: state.table.options.q || undefined,
        sortBy: state.table.options.sortBy,
        descending: state.table.options.descending,
      }

      const response = await PromptApi.getAll(params)
      const { items, total } = response.data

      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", {
        items,
        total,
      })

      // Also load defaults if they haven't been loaded yet
      if (Object.keys(state.defaults.prompts).length === 0) {
        await dispatch("loadDefaults")
      }
    } catch (error) {
      commit("SET_TABLE_LOADING", false)
      console.error("Error fetching prompts:", error)
    }
  }, 500),

  createEditShow({ commit }, prompt) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (prompt) {
      commit("SET_SELECTED", prompt)
    }
  },

  removeShow({ commit }, prompt) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", prompt)
  },

  closeCreateEdit({ commit }) {
    commit("SET_DIALOG_CREATE_EDIT", false)
    commit("RESET_SELECTED")
  },

  closeRemove({ commit }) {
    commit("SET_DIALOG_DELETE", false)
    commit("RESET_SELECTED")
  },

  async save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)

    try {
      const promptData = {
        genai_type: state.selected.genai_type,
        genai_prompt: state.selected.genai_prompt,
        genai_system_message: state.selected.genai_system_message,
        enabled: state.selected.enabled,
        project: state.selected.project,
      }

      if (!state.selected.id) {
        // Create new prompt
        await PromptApi.create(promptData)
        commit(
          "notification_backend/addBeNotification",
          { text: "Prompt created successfully.", type: "success" },
          { root: true }
        )
      } else {
        // Update existing prompt
        await PromptApi.update(state.selected.id, promptData)
        commit(
          "notification_backend/addBeNotification",
          { text: "Prompt updated successfully.", type: "success" },
          { root: true }
        )
      }

      commit("SET_SELECTED_LOADING", false)
      dispatch("closeCreateEdit")
      dispatch("getAll")
    } catch (error) {
      commit("SET_SELECTED_LOADING", false)
      console.error("Error saving prompt:", error)
      commit(
        "notification_backend/addBeNotification",
        { text: "Error saving prompt.", type: "error" },
        { root: true }
      )
    }
  },

  async remove({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)

    try {
      await PromptApi.delete(state.selected.id)

      commit("SET_SELECTED_LOADING", false)
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Prompt deleted successfully.", type: "success" },
        { root: true }
      )
    } catch (error) {
      commit("SET_SELECTED_LOADING", false)
      console.error("Error deleting prompt:", error)
      commit(
        "notification_backend/addBeNotification",
        { text: "Error deleting prompt.", type: "error" },
        { root: true }
      )
    }
  },

  async loadDefaults({ commit }) {
    commit("SET_DEFAULTS_LOADING", true)

    try {
      const response = await PromptApi.getDefaults()
      commit("SET_DEFAULTS", response.data)
    } catch (error) {
      console.error("Error loading default prompts:", error)
    } finally {
      commit("SET_DEFAULTS_LOADING", false)
    }
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
  SET_DEFAULTS(state, value) {
    state.defaults.prompts = value.prompts
    state.defaults.system_messages = value.system_messages
  },
  SET_DEFAULTS_LOADING(state, value) {
    state.defaults.loading = value
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
