import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"
import { GENAI_TYPES } from "@/constants/genai-types"

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

// Mock data
const mockPrompts = [
  {
    id: 1,
    genai_type: 1,
    genai_prompt:
      "Analyze the following tags and recommend additional relevant tags for this incident: {tags}",
    genai_system_message:
      "You are a cybersecurity expert who specializes in incident classification and tagging.",
    enabled: true,
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2024-01-15T10:30:00Z",
    project: { name: "default" },
  },
  {
    id: 2,
    genai_type: 2,
    genai_prompt:
      "Create a comprehensive summary of this incident including timeline, impact, and resolution: {incident_data}",
    genai_system_message:
      "You are a cybersecurity analyst tasked with creating clear, concise incident summaries.",
    enabled: true,
    created_at: "2024-01-16T14:20:00Z",
    updated_at: "2024-01-16T14:20:00Z",
    project: { name: "default" },
  },
  {
    id: 3,
    genai_type: 3,
    genai_prompt:
      "Analyze this signal and provide insights on potential threats and recommended actions: {signal_data}",
    genai_system_message:
      "You are a threat intelligence analyst specializing in signal analysis and threat assessment.",
    enabled: false,
    created_at: "2024-01-17T09:15:00Z",
    updated_at: "2024-01-17T09:15:00Z",
    project: { name: "default" },
  },
  {
    id: 4,
    genai_type: 4,
    genai_prompt: "Summarize the key points from this conversation thread: {conversation_data}",
    genai_system_message:
      "You are a communication specialist who extracts key information from conversations.",
    enabled: true,
    created_at: "2024-01-18T11:45:00Z",
    updated_at: "2024-01-18T11:45:00Z",
    project: { name: "default" },
  },
  {
    id: 5,
    genai_type: 5,
    genai_prompt:
      "Create a tactical report summary with conditions, actions, and needs: {incident_data}",
    genai_system_message:
      "You are a cybersecurity analyst tasked with creating structured tactical reports.",
    enabled: false,
    created_at: "2024-01-19T16:30:00Z",
    updated_at: "2024-01-19T16:30:00Z",
    project: { name: "default" },
  },
]

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
      items: mockPrompts,
      total: mockPrompts.length,
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
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")

    // Simulate API delay
    setTimeout(() => {
      let filteredItems = [...mockPrompts]

      // Apply search filter
      if (state.table.options.q) {
        const searchTerm = state.table.options.q.toLowerCase()
        filteredItems = filteredItems.filter((item) => {
          const typeName = GENAI_TYPES[item.genai_type] || ""
          return (
            typeName.toLowerCase().includes(searchTerm) ||
            item.genai_prompt.toLowerCase().includes(searchTerm) ||
            (item.genai_system_message &&
              item.genai_system_message.toLowerCase().includes(searchTerm))
          )
        })
      }

      // Apply sorting
      if (state.table.options.sortBy.length > 0) {
        const sortBy = state.table.options.sortBy[0]
        const descending = state.table.options.descending[0]

        filteredItems.sort((a, b) => {
          let aVal = a[sortBy]
          let bVal = b[sortBy]

          // Handle genai_type sorting by name
          if (sortBy === "genai_type") {
            aVal = GENAI_TYPES[a.genai_type] || ""
            bVal = GENAI_TYPES[b.genai_type] || ""
          }

          if (aVal < bVal) return descending ? 1 : -1
          if (aVal > bVal) return descending ? -1 : 1
          return 0
        })
      }

      // Apply pagination
      const startIndex = (state.table.options.page - 1) * state.table.options.itemsPerPage
      const endIndex = startIndex + state.table.options.itemsPerPage
      const paginatedItems = filteredItems.slice(startIndex, endIndex)

      commit("SET_TABLE_LOADING", false)
      commit("SET_TABLE_ROWS", {
        items: paginatedItems,
        total: filteredItems.length,
      })
    }, 300)
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

  save({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)

    // Simulate API delay
    setTimeout(() => {
      if (!state.selected.id) {
        // Create new prompt
        const newPrompt = {
          ...state.selected,
          id: Date.now(), // Simple ID generation
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          project: { name: "default" },
        }

        // If enabling this prompt, disable others of the same type
        if (newPrompt.enabled) {
          mockPrompts.forEach((p) => {
            if (p.genai_type === newPrompt.genai_type && p.id !== newPrompt.id) {
              p.enabled = false
            }
          })
        }

        mockPrompts.push(newPrompt)

        commit(
          "notification_backend/addBeNotification",
          { text: "Prompt created successfully.", type: "success" },
          { root: true }
        )
      } else {
        // Update existing prompt
        const index = mockPrompts.findIndex((p) => p.id === state.selected.id)
        if (index !== -1) {
          const updatedPrompt = {
            ...mockPrompts[index],
            ...state.selected,
            updated_at: new Date().toISOString(),
          }

          // If enabling this prompt, disable others of the same type
          if (updatedPrompt.enabled) {
            mockPrompts.forEach((p) => {
              if (p.genai_type === updatedPrompt.genai_type && p.id !== updatedPrompt.id) {
                p.enabled = false
              }
            })
          }

          mockPrompts[index] = updatedPrompt
        }

        commit(
          "notification_backend/addBeNotification",
          { text: "Prompt updated successfully.", type: "success" },
          { root: true }
        )
      }

      commit("SET_SELECTED_LOADING", false)
      dispatch("closeCreateEdit")
      dispatch("getAll")
    }, 500)
  },

  remove({ commit, dispatch }) {
    commit("SET_SELECTED_LOADING", true)

    // Simulate API delay
    setTimeout(() => {
      const index = mockPrompts.findIndex((p) => p.id === state.selected.id)
      if (index !== -1) {
        mockPrompts.splice(index, 1)
      }

      commit("SET_SELECTED_LOADING", false)
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Prompt deleted successfully.", type: "success" },
        { root: true }
      )
    }, 300)
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
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
