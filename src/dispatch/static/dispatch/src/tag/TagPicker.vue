<template>
  <div>
    <span v-click-outside="closeMenu">
      <v-text-field
        readonly
        label="Tags"
        @click="toggleMenu"
        variant="outlined"
        v-model="dummyText"
        class="main-panel"
        :rules="[check_for_error]"
      >
        <template #prepend-inner>
          <v-icon class="panel-button">
            {{ menu ? "mdi-minus" : "mdi-plus" }}
          </v-icon>
        </template>
        <template #append v-if="showCopy">
          <v-icon class="panel-button" @click.stop="copyTags">mdi-content-copy</v-icon>
        </template>
        <div class="form-container mt-2">
          <div class="chip-group" v-show="selectedItems.length">
            <span v-for="(item, index) in selectedItems" :key="item">
              <v-chip
                label
                :key="index"
                :color="item.tag_type?.color"
                closable
                class="tag-chip"
                @click:close="removeItem(item.id)"
              >
                <span class="mr-2">
                  <v-icon
                    v-if="item.tag_type?.icon"
                    :icon="'mdi-' + item.tag_type?.icon"
                    size="18"
                    :style="getColorAsStyle(item.color)"
                  />
                  {{ item.name }}
                </span>
              </v-chip>
            </span>
          </div>
        </div>
      </v-text-field>
      <v-card v-if="menu" class="tag-picker-dropdown-block">
        <!-- Initial state: Show generate button -->
        <div
          v-if="
            !suggestionsGenerated && props.visibility !== 'Restricted' && props.showGenAISuggestions
          "
          class="mb-4"
        >
          <div class="gradient-border-wrapper">
            <div class="white-bg-wrapper">
              <v-btn
                variant="flat"
                size="small"
                @click="generateSuggestions"
                :loading="suggestionsLoading"
                class="generate-suggestions-btn"
                :style="{
                  backgroundColor: '#ffffff !important',
                  background: '#ffffff !important',
                  color: '#1a1a1a !important',
                }"
              >
                <v-icon start size="18" color="#ffc107">mdi-sparkles</v-icon>
                <span class="generate-btn-text">Generate AI tag suggestions</span>
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Error banner: Show when there's an error -->
        <div
          v-if="suggestionsGenerated && suggestionsError && props.showGenAISuggestions"
          class="error-banner mb-3"
        >
          <div class="error-content">
            <v-icon size="18" color="#f57f17" class="mr-2">mdi-alert</v-icon>
            <span class="error-message">{{ suggestionsError }}</span>
            <v-btn
              variant="text"
              size="small"
              @click="retryGenerateSuggestions"
              :loading="suggestionsLoading"
              class="retry-btn ml-3"
            >
              <v-icon start size="16">mdi-refresh</v-icon>
              Try Again
            </v-btn>
          </div>
        </div>

        <!-- No project error banner -->
        <div v-if="noProjectError" class="error-banner mb-3">
          <div class="error-content">
            <v-icon size="18" color="#f57f17" class="mr-2">mdi-alert</v-icon>
            <span class="error-message">{{ noProjectError }}</span>
          </div>
        </div>

        <!-- Suggestions panel: Show when generated (expanded or collapsed) -->
        <div
          v-if="suggestionsGenerated && tagSuggestions.length > 0 && props.showGenAISuggestions"
          :class="[
            'mitre-suggestions-panel',
            suggestionsExpanded ? 'mb-4' : 'mb-3',
            { collapsed: !suggestionsExpanded },
          ]"
        >
          <div :class="suggestionsExpanded ? 'suggestion-header mb-1' : 'suggestion-header mb-0'">
            <div
              class="suggestion-title clickable"
              @click="suggestionsExpanded = !suggestionsExpanded"
              :title="suggestionsExpanded ? 'Collapse suggestions' : 'Expand suggestions'"
            >
              GenAI suggests the following tags:
            </div>
            <v-btn
              icon
              size="small"
              variant="text"
              @click="suggestionsExpanded = !suggestionsExpanded"
              class="collapse-btn"
              :title="suggestionsExpanded ? 'Collapse suggestions' : 'Expand suggestions'"
            >
              <v-icon size="18">
                {{ suggestionsExpanded ? "mdi-chevron-up" : "mdi-chevron-down" }}
              </v-icon>
            </v-btn>
          </div>

          <!-- Suggestion content - only show when expanded -->
          <transition name="suggestion-collapse">
            <div v-show="suggestionsExpanded" class="suggestion-content">
              <div
                v-for="(group, groupIdx) in tagSuggestions"
                :key="'suggested-group-' + groupIdx"
                class="suggestion-group mb-1"
              >
                <span class="suggestion-group-label">
                  <span>{{ getTagType(group.tag_type_id).name }}</span
                  >:
                </span>
                <span
                  v-for="tag in group.tags"
                  :key="'suggested-tag-' + tag.id"
                  class="suggestion-chip-wrapper"
                >
                  <v-chip
                    class="suggestion-chip tag-chip mr-1"
                    :color="getTagType(group.tag_type_id).color || '#e0e0e0'"
                    size="small"
                    label
                    rounded
                    :title="tag.reason"
                    @click="addSuggestedTag(tag)"
                  >
                    <v-icon
                      start
                      size="16"
                      :color="'#fff'"
                      v-if="getTagType(group.tag_type_id).icon"
                      class="tag-type-icon"
                    >
                      mdi-{{ getTagType(group.tag_type_id).icon }}
                    </v-icon>
                    {{ tag.name }}
                    <v-icon class="add-chip ml-1" size="16">mdi-plus</v-icon>
                  </v-chip>
                </span>
              </div>
              <div class="suggestion-help-text mt-2">
                <v-icon size="16" color="#ffc107" class="mr-1">mdi-lightbulb-on-outline</v-icon>
                Tip: Hover over a suggested tag to see why it was recommended.
              </div>
            </div>
          </transition>
        </div>

        <!-- Regular tag picker - always visible when menu is open -->
        <div>
          <v-text-field
            hide-details
            type="text"
            class="dropdown-input"
            placeholder="🔍  Search tags..."
            v-model="searchQuery"
            @update:model-value="performSearch"
            @focus="showDropdown(true)"
          />
          <ul class="dropdown-box">
            <div class="empty-search" v-if="!filteredMenuItems.length && searchQuery.length">
              <p>
                No tags containing <span class="search-term">{{ searchQuery }}</span> found.
              </p>
            </div>
            <div :key="groupIndex" v-for="(group, groupIndex) in groups">
              <!-- Check if the group has any items in filteredMenuItems -->
              <div
                class="tag-group-container"
                v-if="
                  !searchQuery.length ||
                  filteredMenuItems.some((filteredItem) => group.menuItems.includes(filteredItem))
                "
              >
                <input :id="'togList' + group.id" type="checkbox" checked />
                <label :for="'togList' + group.id">
                  <div class="tag-group-metadata">
                    <span class="tag-group-header">
                      <v-icon
                        v-if="group.icon"
                        :icon="'mdi-' + group.icon"
                        size="18"
                        :color="group.color"
                        class="tag-type-icon"
                      />
                      <strong v-text="group.label" />
                      <span v-show="group.isRequired" class="tag-group-rule">Required</span>
                      <span v-show="group.isExclusive" class="tag-group-rule">Exclusive</span>
                      <span class="tag-group-icon-down"><v-icon>mdi-chevron-down</v-icon></span>
                      <v-icon class="tag-group-icon-up">mdi-chevron-up</v-icon>
                    </span>

                    <span class="tag-group-desc" v-text="group.desc" />
                    <span
                      class="tag-group-rule-desc"
                      v-show="
                        group.isExclusive &&
                        selectedItems.some((item) => item.tag_type.id === group.id)
                      "
                    >
                      Only 1 tag allowed for this category
                    </span>
                  </div>
                </label>
                <label v-for="(item, index) in group.menuItems" :key="index" class="checkbox-label">
                  <li
                    class="checkbox-item"
                    v-if="!filteredMenuItems.length || filteredMenuItems.includes(item)"
                  >
                    <input
                      type="checkbox"
                      v-model="selectedItems"
                      :id="item.id"
                      :value="item"
                      :disabled="group.isExclusive && isItemDisabled(group, item)"
                      class="checkbox-item-box"
                    />
                    {{ item.name }}
                  </li>
                </label>
                <v-divider v-if="groupIndex < groups.length - 1" class="mt-2 mb-2" />
              </div>
            </div>
          </ul>
        </div>
      </v-card>
    </span>
    <v-snackbar v-model="snackbar" :timeout="2400" color="success">
      <v-row class="fill-height" align="center">
        <v-col class="text-center">Tags copied to the clipboard</v-col>
      </v-row>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { cloneDeep } from "lodash"
import { useStore } from "vuex"

const store = useStore()
const menu = ref(false)
const dummyText = ref(" ")
const searchQuery = ref("")
const filteredMenuItems = ref([])
const isDropdownOpen = ref(false)
const snackbar = ref(false)
const suggestionsExpanded = ref(false)
const error = ref(null)
const noProjectError = ref(null)

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  project: {
    type: Object,
    default: null,
  },
  model: {
    type: String,
    default: null,
  },
  modelId: {
    type: Number,
    default: null,
  },
  showCopy: {
    type: Boolean,
    default: false,
  },
  visibility: {
    type: String,
    default: null,
  },
  showGenAISuggestions: {
    type: Boolean,
    default: false,
  },
  modelType: {
    type: String,
    default: "incident", // "incident" or "case"
  },
})

// Computed properties from store
const groups = computed(() => store.state.tag.groups)
const suggestionsLoading = computed(() => store.state.tag.suggestionsLoading)
const suggestionsGenerated = computed(() => store.state.tag.suggestionsGenerated)
const suggestionsError = computed(() => store.state.tag.suggestionsError)
const tagSuggestions = computed(() => store.state.tag.tagSuggestions)

// Selected items computed
const selectedItems = computed({
  get: () => cloneDeep(props.modelValue),
  set: (value) => {
    const tags = value.filter((v) => typeof v !== "string")
    emit("update:modelValue", tags)
    validateTags(tags)
  },
})

const emit = defineEmits(["update:modelValue"])

// Validation function
const check_for_error = () => {
  return error.value
}

function are_required_tags_selected(sel) {
  // iterate through all tag types and ensure that at least one tag of each required tag type is selected
  const tagTypes = Object.values(groups.value)
  for (let i = 0; i < tagTypes.length; i++) {
    if (tagTypes[i].isRequired) {
      if (!sel.some((item) => item.tag_type?.id === tagTypes[i]?.id)) {
        return false
      }
    }
  }
  return true
}

function validateTags(value) {
  // Don't validate if groups haven't been loaded yet
  if (!groups.value || Object.keys(groups.value).length === 0) {
    return
  }

  // Handle both single project object and array of projects
  const projects = Array.isArray(props.project) ? props.project : [props.project]
  const validProjects = projects.filter((p) => p && p.name)

  if (!validProjects.length) {
    error.value = true
    dummyText.value += " "
    return
  }

  // Check if all tags belong to any of the selected projects
  const all_tags_in_projects = value.every((tag) => {
    return validProjects.some((project) => {
      if (project.id && tag.project?.id) {
        return tag.project.id === project.id
      } else if (project.name && tag.project?.name) {
        return tag.project.name === project.name
      }
      return false
    })
  })

  if (all_tags_in_projects) {
    const requiredSelected = are_required_tags_selected(value)

    if (!requiredSelected) {
      const required_tag_types = Object.values(groups.value)
        .filter((tag_type) => tag_type.isRequired)
        .map((tag_type) => tag_type.label)
      error.value = `Please select at least one tag from each required category (${required_tag_types.join(
        ", "
      )})`
    } else {
      error.value = null
    }
  } else {
    error.value = "Only tags in selected projects are allowed"
  }
  dummyText.value += " "
}

// Methods
const fetchData = async () => {
  // Handle both single project object and array of projects
  const projects = Array.isArray(props.project) ? props.project : [props.project]
  const validProjects = projects.filter((p) => p && p.name)

  if (!validProjects.length) {
    // Show error message when no projects are selected
    store.commit("tag/SET_TABLE_ROWS", { items: [], total: 0 })
    store.commit("tag/SET_GROUPS", {})
    noProjectError.value = "You must select a project to view tags"
    return
  }

  // Clear any previous error when we have valid projects
  noProjectError.value = null

  // Let the store handle all the logic for single or multiple projects
  await store.dispatch("tag/fetchTags", {
    project: validProjects,
    model: props.model,
  })
}

const fetchTagTypes = async () => {
  await store.dispatch("tag/fetchTagTypes")
}

const generateSuggestions = async () => {
  // Handle both single project object and array of projects
  const project = Array.isArray(props.project) ? props.project[0] : props.project
  if (!project?.id) return
  await store.dispatch("tag/generateSuggestions", {
    projectId: project.id,
    modelId: props.modelId,
    modelType: props.modelType,
  })
}

const addSuggestedTag = (tag) => {
  if (!tag || !tag.id) return
  const fullTag = store.state.tag.table.rows.items.find((t) => t.id === tag.id)
  if (!fullTag) return
  if (!selectedItems.value.some((item) => item.id === fullTag.id)) {
    selectedItems.value = [...selectedItems.value, fullTag]
  }
}

const getTagType = (tagTypeId) => {
  return store.state.tag.tagTypes[tagTypeId] || {}
}

const copyTags = () => {
  const tags = selectedItems.value.map((item) => `${item.tag_type.name}/${item.name}`)
  navigator.clipboard.writeText(tags.join(", "))
  snackbar.value = true
}

const closeMenu = () => {
  menu.value = false
}

const toggleMenu = () => {
  menu.value = !menu.value
}

const showDropdown = (state) => {
  isDropdownOpen.value = state
}

const removeItem = (index) => {
  const value = selectedItems.value.filter((item) => item.id !== index)
  selectedItems.value = value
  validateTags(value)
}

const performSearch = () => {
  filteredMenuItems.value = []
  groups.value.forEach((group) => {
    const filteredItems = group.menuItems.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    filteredMenuItems.value.push(...filteredItems)
  })
}

const isItemDisabled = (group, item) => {
  const isItemSelectedInGroup = selectedItems.value.some(
    (selectedItem) => selectedItem.tag_type.id === group.id
  )
  return (
    isItemSelectedInGroup &&
    !selectedItems.value.some((selectedItem) => selectedItem.id === item.id)
  )
}

// Lifecycle hooks
onMounted(() => {
  fetchData()
  fetchTagTypes()
  // Don't validate initially - wait for groups to be loaded
})

watch(
  () => props.project,
  (newVal) => {
    if (newVal) {
      fetchData()
      // Validate after project changes
      validateTags(selectedItems.value)
    }
  }
)

// Watch for groups to be loaded and validate
watch(
  () => groups.value,
  (newGroups) => {
    if (newGroups && Object.keys(newGroups).length > 0) {
      validateTags(selectedItems.value)
    }
  },
  { immediate: true }
)

// When suggestions are generated, expand the suggestions box by default
watch(
  () => suggestionsGenerated.value,
  (newVal) => {
    if (newVal) {
      suggestionsExpanded.value = true
    }
  }
)

// Reset suggestions when the incident/model changes
watch(
  () => props.modelId,
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      store.dispatch("tag/resetSuggestions")
      suggestionsExpanded.value = false
    }
  }
)

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = function (event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.body.addEventListener("click", el.clickOutsideEvent, { passive: true })
  },
  unmounted(el) {
    document.body.removeEventListener("click", el.clickOutsideEvent)
  },
}

function retryGenerateSuggestions() {
  store.dispatch("tag/resetSuggestions")
  generateSuggestions()
}

function getColorAsStyle(color) {
  return color ? { backgroundColor: color } : {}
}
</script>

<style scoped src="@/styles/tagpicker.scss"></style>
