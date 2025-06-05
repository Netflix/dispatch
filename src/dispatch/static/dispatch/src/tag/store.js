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
      },
    },
    loading: false,
  },
  suggestedTags: [],
  selectedItems: [],
  validationError: null,
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
  removeTag({ commit, state }, tagId) {
    commit("REMOVE_SELECTED_TAG", tagId)
  },
  validateTags({ commit, state }, { value, groups, currentProject }) {
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
      if (areRequiredTagsSelected(value, groups)) {
        commit("SET_VALIDATION_ERROR", true)
      } else {
        const required_tag_types = groups
          .filter((tag_type) => tag_type.isRequired)
          .map((tag_type) => tag_type.label)
        commit(
          "SET_VALIDATION_ERROR",
          `Please select at least one tag from each required category (${required_tag_types.join(
            ", "
          )})`
        )
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
    console.log("Eligible tag type IDs:", eligibleTagTypeIds)
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
    console.log(
      "Filtered tags:",
      tags.map((t) => t.tag_type.name)
    )
    commit("SET_TABLE_ROWS", { items: tags, total: tags.length })
    return tags
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
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
