import { getField, updateField } from "vuex-map-fields"
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"
import TagApi from "@/tag/api"
import TagTypeApi from "@/tag_type/api"

const getDefaultSelectedState = () => {
  return {
    name: null,
    source: "dispatch",
    tag_type: null,
    uri: null,
    id: null,
    description: "Generic tag",
    external_id: null,
    project: null,
    created_at: null,
    discoverable: null,
    updated_at: null,
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
      total: null,
    },
    options: {
      q: "",
      page: 1,
      itemsPerPage: 25,
      sortBy: ["name"],
      descending: [false],
      filters: {
        project: [],
        tag_type: [],
        discoverable: [],
      },
    },
    loading: false,
  },
  suggestedTags: [],
  selectedItems: [],
  validationError: null,
  tagTypes: {},
  groups: [],
  loading: false,
  more: false,
  total: 0,
  suggestionsLoading: false,
  suggestionsGenerated: false,
  suggestionsError: null,
  tagSuggestions: [],
}

const getters = {
  getField,
}

const actions = {
  getAll: debounce(({ commit, state }) => {
    commit("SET_TABLE_LOADING", "primary")
    let params = SearchUtils.createParametersFromTableOptions({ ...state.table.options }, "Tag")
    return TagApi.getAll(params)
      .then((response) => {
        commit("SET_TABLE_LOADING", false)
        commit("SET_TABLE_ROWS", response.data)
      })
      .catch(() => {
        commit("SET_TABLE_LOADING", false)
      })
  }, 500),
  createEditShow({ commit }, Tag) {
    commit("SET_DIALOG_CREATE_EDIT", true)
    if (Tag) {
      commit("SET_SELECTED", Tag)
    }
  },
  removeShow({ commit }, Tag) {
    commit("SET_DIALOG_DELETE", true)
    commit("SET_SELECTED", Tag)
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
    if (!state.selected.id) {
      return TagApi.create(state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Tag created successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    } else {
      return TagApi.update(state.selected.id, state.selected)
        .then(() => {
          commit("SET_SELECTED_LOADING", false)
          dispatch("closeCreateEdit")
          dispatch("getAll")
          commit(
            "notification_backend/addBeNotification",
            { text: "Tag updated successfully.", type: "success" },
            { root: true }
          )
        })
        .catch(() => {
          commit("SET_SELECTED_LOADING", false)
        })
    }
  },
  remove({ commit, dispatch }) {
    return TagApi.delete(state.selected.id).then(function () {
      dispatch("closeRemove")
      dispatch("getAll")
      commit(
        "notification_backend/addBeNotification",
        { text: "Tag deleted successfully.", type: "success" },
        { root: true }
      )
    })
  },
  async fetchSuggestedTags({ commit }, suggestedTagData) {
    // Fetch all tag and tag_type data needed for the suggestions
    const tagTypeIds = suggestedTagData.map((g) => g.tag_type_id)
    const tagIds = suggestedTagData.flatMap((g) => g.tags.map((t) => t.id))
    const tagFilterOptions = {
      filters: {
        tagIdFilter: tagIds.map((id) => ({ model: "Tag", field: "id", op: "==", value: id })),
        tagTypeIdFilter: tagTypeIds.map((id) => ({
          model: "TagType",
          field: "id",
          op: "==",
          value: id,
        })),
      },
      itemsPerPage: 100,
    }
    const params = SearchUtils.createParametersFromTableOptions({ ...tagFilterOptions })
    const tagResp = await TagApi.getAll(params)
    const tags = tagResp.data.items
    // Group tags by tag_type_id
    const tagTypeMap = {}
    tags.forEach((tag) => {
      if (tag.tag_type && tag.tag_type.id) {
        tagTypeMap[tag.tag_type.id] = tag.tag_type
      }
    })
    // Also ensure all tag_types are present (in case some are not attached to tags)
    suggestedTagData.forEach((group) => {
      if (!tagTypeMap[group.tag_type_id]) {
        tagTypeMap[group.tag_type_id] = {
          id: group.tag_type_id,
          name: "",
          icon: "",
          color: "#1976d2",
        }
      }
    })
    // Build the suggestion structure for rendering
    const result = suggestedTagData.map((group) => {
      const tag_type = tagTypeMap[group.tag_type_id]
      return {
        tag_type,
        tags: group.tags.map((t) => {
          const tag = tags.find((tg) => tg.id === t.id)
          return {
            ...t,
            tag,
          }
        }),
      }
    })
    commit("SET_SUGGESTED_TAGS", result)
  },
  addSuggestedTag({ commit, state }, tagObj) {
    if (!tagObj || !tagObj.id) return
    if (!state.selectedItems.some((item) => item.id === tagObj.id)) {
      commit("ADD_SELECTED_TAG", tagObj)
    }
  },
  removeTag({ commit }, tagId) {
    commit("REMOVE_SELECTED_TAG", tagId)
  },
  validateTags({ commit }, { value, groups, currentProject }) {
    // project_id logic
    const project_id = currentProject?.id || 0
    let all_tags_in_project = false
    if (project_id) {
      all_tags_in_project = value.every((tag) => tag.project?.id == project_id)
    } else {
      const project_name = currentProject?.name
      if (!project_name) {
        commit("SET_VALIDATION_ERROR", true)
        return
      }
      all_tags_in_project = value.every((tag) => tag.project?.name == project_name)
    }
    if (all_tags_in_project) {
      if (!areRequiredTagsSelected(value, groups)) {
        const required_tag_types = groups
          .filter((tag_type) => tag_type.isRequired)
          .map((tag_type) => tag_type.label)
        commit(
          "SET_VALIDATION_ERROR",
          `Please select at least one tag from each required category (${required_tag_types.join(
            ", "
          )})`
        )
      } else {
        commit("SET_VALIDATION_ERROR", null)
      }
    } else {
      commit("SET_VALIDATION_ERROR", "Only tags in selected project are allowed")
    }
  },
  async fetchEligibleTagTypes() {
    // Fetch all tag types where any discoverable_* is true
    const discoverableFields = [
      "discoverable_incident",
      "discoverable_case",
      "discoverable_signal",
      "discoverable_query",
      "discoverable_source",
      "discoverable_document",
    ]
    const orFilters = discoverableFields.map((field) => ({ field, op: "==", value: true }))
    const params = {
      filters: { or: orFilters },
      itemsPerPage: 5000, // adjust as needed
    }
    const resp = await TagTypeApi.getAll(params)
    return resp.data.items.map((tt) => tt.id)
  },

  async fetchAllTagsWithEligibleTypes({ commit, dispatch }, { project }) {
    // 1. Fetch eligible tag type ids
    const eligibleTagTypeIds = await dispatch("fetchEligibleTagTypes")
    // 2. Fetch tags for this project
    const tagFilterOptions = {
      filters: {
        project: [{ model: "Project", field: "name", op: "==", value: project.name }],
        tagTypeIdFilter: eligibleTagTypeIds.map((id) => ({
          model: "TagType",
          field: "id",
          op: "==",
          value: id,
        })),
        tagFilter: [{ model: "Tag", field: "discoverable", op: "==", value: "true" }],
      },
      itemsPerPage: 5000, // adjust as needed
    }
    const params = SearchUtils.createParametersFromTableOptions({ ...tagFilterOptions })
    const tagResp = await TagApi.getAll(params)
    // 3. Filter tags client-side as a safeguard
    const tags = tagResp.data.items.filter((tag) => eligibleTagTypeIds.includes(tag.tag_type.id))

    commit("SET_TABLE_ROWS", { items: tags, total: tags.length })
    return tags
  },

  async fetchTags({ commit, dispatch }, { project, model }) {
    // Handle both single project object and array of projects
    const projects = Array.isArray(project) ? project : [project]
    const validProjects = projects.filter((p) => p && p.name)

    if (!validProjects.length) {
      commit("SET_TABLE_ROWS", { items: [], total: 0 })
      commit("SET_GROUPS", {})
      return []
    }

    commit("SET_LOADING", true)

    try {
      let relevantTagTypeIds = []

      // If model is specified, first fetch the relevant TagType IDs
      if (model) {
        const tagTypeFilterOptions = {
          filter: JSON.stringify([
            {
              and: [{ model: "TagType", field: "discoverable_" + model, op: "==", value: "true" }],
            },
          ]),
          itemsPerPage: -1,
          fields: JSON.stringify(["id"]),
        }

        const tagTypeResponse = await TagTypeApi.getAll(tagTypeFilterOptions)
        relevantTagTypeIds = tagTypeResponse.data.items.map((tt) => tt.id)

        if (!relevantTagTypeIds.length) {
          commit("SET_TABLE_ROWS", { items: [], total: 0 })
          commit("SET_GROUPS", {})
          commit("SET_LOADING", false)
          return []
        }
      }

      // Fetch tags for each project and combine them
      const allTags = []
      for (const singleProject of validProjects) {
        const projectTags = await dispatch("fetchTagsForSingleProject", {
          project: singleProject,
          relevantTagTypeIds,
          model,
        })
        if (projectTags) {
          allTags.push(...projectTags)
        }
      }
      // Update the store with combined results
      commit("SET_TABLE_ROWS", { items: allTags, total: allTags.length })
      commit("SET_GROUPS", convertData(allTags))
      commit("SET_LOADING", false)
      return allTags
    } catch (error) {
      console.error("Error fetching tags:", error)
      commit("SET_LOADING", false)
      throw error
    }
  },

  async fetchTagsForSingleProject(_, { project, relevantTagTypeIds, model }) {
    // Build the tag filter options using the same direct approach as tagTypeFilterOptions
    let baseFilters = [{ model: "Tag", field: "discoverable", op: "==", value: "true" }]

    // Add project filter if project is defined
    if (project && project.name) {
      baseFilters.unshift({ model: "Project", field: "name", op: "==", value: project.name })
    }

    let tagFilterOptions = {
      filter: JSON.stringify([
        {
          and: baseFilters,
        },
      ]),
      itemsPerPage: 500,
      sortBy: ["tag_type.name"],
      sortDesc: [false],
    }

    // If we have relevant tag type IDs, add the filter
    if (model && relevantTagTypeIds.length > 0) {
      baseFilters.push({
        model: "Tag",
        field: "tag_type_id",
        op: "in",
        value: relevantTagTypeIds,
      })
      tagFilterOptions.filter = JSON.stringify([
        {
          and: baseFilters,
        },
      ])
    }

    const response = await TagApi.getAll(tagFilterOptions)
    return response.data.items
  },

  async fetchTagTypes({ commit }) {
    try {
      const resp = await TagTypeApi.getAll({ itemsPerPage: 5000 })
      const tagTypes = Object.fromEntries(resp.data.items.map((tt) => [tt.id, tt]))

      // Add sample tag types for demo purposes if they don't exist
      if (!tagTypes[135]) {
        tagTypes[135] = {
          id: 135,
          name: "MITRE Tactics",
          color: "#1976d2",
          icon: "bullseye-arrow",
        }
      }
      if (!tagTypes[136]) {
        tagTypes[136] = {
          id: 136,
          name: "MITRE Techniques",
          color: "#388e3c",
          icon: "tools",
        }
      }

      commit("SET_TAG_TYPES", tagTypes)
      return tagTypes
    } catch (error) {
      console.error("Error fetching tag types:", error)
      throw error
    }
  },

  async generateSuggestions({ commit }, { projectId, modelId, modelType = "incident" }) {
    commit("SET_SUGGESTIONS_LOADING", true)
    commit("SET_SUGGESTIONS_ERROR", null)

    try {
      let response
      if (modelType === "case") {
        response = await TagApi.getRecommendationsCase(projectId, modelId)
      } else {
        response = await TagApi.getRecommendationsIncident(projectId, modelId)
      }

      const errorMessage = response.data?.error_message || response.error_message
      if (errorMessage) {
        commit("SET_SUGGESTIONS_ERROR", errorMessage)
        commit("SET_TAG_SUGGESTIONS", [])
        return
      }

      const suggestions = response.data?.recommendations || response.recommendations || []
      commit("SET_TAG_SUGGESTIONS", Array.isArray(suggestions) ? suggestions : [])
      commit("SET_SUGGESTIONS_GENERATED", true)
    } catch (error) {
      console.error("Error generating AI suggestions:", error)
      commit(
        "SET_SUGGESTIONS_ERROR",
        "Failed to generate AI tag suggestions. Please try again later."
      )
      commit("SET_TAG_SUGGESTIONS", [])
    } finally {
      commit("SET_SUGGESTIONS_LOADING", false)
      commit("SET_SUGGESTIONS_GENERATED", true)
    }
  },

  resetSuggestions({ commit }) {
    commit("SET_SUGGESTIONS_GENERATED", false)
    commit("SET_SUGGESTIONS_ERROR", null)
  },

  getTagType({ state }, tagTypeId) {
    return state.tagTypes[tagTypeId] || {}
  },

  convertDataAndSetGroups({ commit }, data) {
    commit("SET_GROUPS", convertData(data))
  },
}

function areRequiredTagsSelected(sel, tagTypes) {
  for (let i = 0; i < tagTypes.length; i++) {
    if (tagTypes[i].isRequired) {
      if (!sel.some((item) => item.tag_type?.id === tagTypes[i]?.id)) {
        return false
      }
    }
  }
  return true
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
  SET_SUGGESTED_TAGS(state, tags) {
    state.suggestedTags = tags
  },
  ADD_SELECTED_TAG(state, tag) {
    state.selectedItems = [...(state.selectedItems || []), tag]
  },
  REMOVE_SELECTED_TAG(state, tagId) {
    state.selectedItems = (state.selectedItems || []).filter((item) => item.id !== tagId)
  },
  SET_VALIDATION_ERROR(state, error) {
    state.validationError = error
  },
  SET_LOADING(state, value) {
    state.loading = value
  },
  SET_MORE(state, value) {
    state.more = value
  },
  SET_TOTAL(state, value) {
    state.total = value
  },
  SET_GROUPS(state, groups) {
    state.groups = groups
  },
  SET_TAG_TYPES(state, types) {
    state.tagTypes = types
  },
  SET_SUGGESTIONS_LOADING(state, value) {
    state.suggestionsLoading = value
  },
  SET_SUGGESTIONS_GENERATED(state, value) {
    state.suggestionsGenerated = value
  },
  SET_SUGGESTIONS_ERROR(state, error) {
    state.suggestionsError = error
  },
  SET_TAG_SUGGESTIONS(state, suggestions) {
    state.tagSuggestions = suggestions
  },
}

// Helper function for converting data
function convertData(data) {
  return data.reduce((r, a) => {
    if (!r[a.tag_type.id]) {
      r[a.tag_type.id] = {
        id: a.tag_type.id,
        icon: a.tag_type.icon,
        label: a.tag_type.name,
        desc: a.tag_type.description,
        color: a.tag_type.color,
        isRequired: a.tag_type.required,
        isExclusive: a.tag_type.exclusive,
        menuItems: [],
      }
    }
    r[a.tag_type.id].menuItems.push(a)
    return r
  }, Object.create(null))
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
