<template>
  <div>
    <div v-click-outside="closeMenu">
      <span class="tag-picker-row">
        <div class="tag-picker-outline">
          <v-icon class="panel-button tag-add-icon" @click="toggleMenu" style="cursor: pointer">{{
            menu ? "mdi-minus" : "mdi-plus"
          }}</v-icon>
          <div class="tag-picker-label">Tags</div>
          <div class="chip-group" v-show="selectedItems.length">
            <span v-for="(item, index) in selectedItems" :key="item">
              <v-chip
                label
                :key="index"
                closable
                class="tag-chip"
                size="small"
                @click:close="removeItem(item.id)"
                :style="{
                  backgroundColor: (item.tag_type?.color || '#e0e0e0') + '22',
                  color: item.tag_type?.color || '#333',
                }"
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
        <v-icon
          v-if="showCopy"
          class="panel-button tag-copy-icon"
          @click.stop="copyTags"
          style="cursor: pointer"
          >mdi-content-copy</v-icon
        >
      </span>
      <v-card v-if="menu" class="tag-picker-dropdown-block">
        <!-- Initial state: Show generate button -->
        <div v-if="!suggestionsGenerated" class="mb-4">
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

        <!-- Suggestions panel: Show when generated (expanded or collapsed) -->
        <div
          v-if="suggestionsGenerated && tagSuggestions.length > 0"
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
            <div v-if="suggestionsExpanded" class="suggestion-content">
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
                    :style="{
                      backgroundColor: (getTagType(group.tag_type_id).color || '#e0e0e0') + '22',
                      color: getTagType(group.tag_type_id).color || '#333',
                      cursor: 'pointer',
                    }"
                    size="small"
                    label
                    rounded
                    :title="tag.reason"
                    @click="addSuggestedTag(tag)"
                  >
                    <v-icon
                      start
                      size="16"
                      :color="getTagType(group.tag_type_id).color"
                      v-if="getTagType(group.tag_type_id).icon"
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
                        :style="getBackgroundColorAsStyle(group.color)"
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
    </div>
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
import TagApi from "@/tag/api"
import SearchUtils from "@/search/utils"
import TagTypeApi from "@/tag_type/api"

const menu = ref(false)
const dummyText = ref(" ")
const items = ref([])
const total = ref(0)
const groups = ref([])
const searchQuery = ref("")
const filteredMenuItems = ref([])
const isDropdownOpen = ref(false)
const error = ref(true)
const snackbar = ref(false)
const loading = ref(false)
const more = ref(false)
const tagTypes = ref({})
const suggestionsExpanded = ref(false)
const suggestionsLoading = ref(false)
const suggestionsGenerated = ref(false)

const props = defineProps({
  modelValue: {
    type: Array,
    default: function () {
      return []
    },
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
})
const currentProject = ref(props.project)

const fetchData = () => {
  if (!currentProject.value) {
    return
  }
  loading.value = true

  let filterOptions = {
    q: null,
    itemsPerPage: 500,
    sortBy: ["tag_type.name"],
    descending: [false],
  }

  let filters = {}

  filters["project"] = [
    { model: "Project", field: "name", op: "==", value: currentProject.value.name },
  ]

  // add a filter to only return discoverable tags
  filters["tagFilter"] = [{ model: "Tag", field: "discoverable", op: "==", value: "true" }]

  // Simplified tag type filtering - only filter by model if specified
  if (props.model) {
    filters["tagTypeFilter"] = [
      { model: "TagType", field: "discoverable_" + props.model, op: "==", value: "true" },
    ]
  }

  filterOptions = {
    ...filterOptions,
    filters: filters,
  }

  filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

  TagApi.getAll(filterOptions)
    .then((response) => {
      items.value = response.data.items
      total.value = response.data.total

      if (items.value.length < total.value) {
        more.value = true
      } else {
        more.value = false
      }
      groups.value = convertData(items.value)
      loading.value = false
      validateTags(selectedItems.value)
    })
    .catch((error) => {
      console.error("Error fetching tags:", error)
      loading.value = false
    })
}

async function fetchTagTypes() {
  const resp = await TagTypeApi.getAll({ itemsPerPage: 5000 })
  tagTypes.value = Object.fromEntries(resp.data.items.map((tt) => [tt.id, tt]))

  // Add sample tag types for demo purposes if they don't exist
  if (!tagTypes.value[135]) {
    tagTypes.value[135] = {
      id: 135,
      name: "MITRE Tactics",
      color: "#1976d2",
      icon: "bullseye-arrow",
    }
  }
  if (!tagTypes.value[136]) {
    tagTypes.value[136] = {
      id: 136,
      name: "MITRE Techniques",
      color: "#388e3c",
      icon: "tools",
    }
  }
}

onMounted(fetchData)
onMounted(fetchTagTypes)

watch(
  () => props.project,
  (newVal) => {
    if (newVal === currentProject.value) {
      return
    }
    currentProject.value = newVal
    fetchData()
    validateTags(selectedItems.value)
  }
)

function are_required_tags_selected(sel) {
  // iterate through all tag types and ensure that at least one tag of each required tag type is selected
  const tagTypes = groups.value
  for (let i = 0; i < tagTypes.length; i++) {
    if (tagTypes[i].isRequired) {
      if (!sel.some((item) => item.tag_type?.id === tagTypes[i]?.id)) {
        return false
      }
    }
  }
  return true
}

const emit = defineEmits(["update:modelValue"])

function validateTags(value) {
  const project_id = currentProject.value?.id || 0
  var all_tags_in_project = false
  if (project_id) {
    all_tags_in_project = value.every((tag) => tag.project?.id == project_id)
  } else {
    const project_name = currentProject.value?.name
    if (!project_name) {
      error.value = true
      dummyText.value += " "
      return
    }
    all_tags_in_project = value.every((tag) => tag.project?.name == project_name)
  }
  if (all_tags_in_project) {
    if (are_required_tags_selected(value)) {
      error.value = true
    } else {
      const required_tag_types = groups.value
        .filter((tag_type) => tag_type.isRequired)
        .map((tag_type) => tag_type.label)
      error.value = `Please select at least one tag from each required category (${required_tag_types.join(
        ", "
      )})`
    }
  } else {
    error.value = "Only tags in selected project are allowed"
  }
  dummyText.value += " "
}

const selectedItems = computed({
  get: () => cloneDeep(props.modelValue),
  set: (value) => {
    const tags = value.filter((v) => {
      if (typeof v === "string") {
        return false
      }
      return true
    })
    emit("update:modelValue", tags)
    // check to make sure all tags in project
    validateTags(value)
  },
})

const copyTags = () => {
  const tags = selectedItems.value.map((item) => `${item.tag_type.name}/${item.name}`)
  navigator.clipboard.writeText(tags.join(", "))
  snackbar.value = true
}

const closeMenu = () => {
  menu.value = false
}

const toggleMenu = () => {
  console.log("Toggle menu clicked, current menu state:", menu.value)
  menu.value = !menu.value
  console.log("New menu state:", menu.value)
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

const getColorAsStyle = (color) => {
  return `color: '${color}'`
}

const getBackgroundColorAsStyle = (color) => {
  return `background-color: '${color}'`
}

const convertData = (data) => {
  var groupedObject = data.reduce(function (r, a) {
    // Filter out tag types where all discoverability fields are false
    const tagType = a.tag_type
    const hasAnyDiscoverability =
      tagType.discoverable_incident ||
      tagType.discoverable_case ||
      tagType.discoverable_signal ||
      tagType.discoverable_query ||
      tagType.discoverable_source ||
      tagType.discoverable_document

    if (!hasAnyDiscoverability) {
      return r // Skip this tag type
    }

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
  var temp = Object.keys(groupedObject).map(function (key) {
    return groupedObject[key]
  })
  return temp
}

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

// Tag suggestions from API - make reactive so it can be updated from API
const tagSuggestions = ref([])

function addSuggestedTag(tag) {
  if (!tag || !tag.id) return
  // Find the full tag object from items.value
  const fullTag = items.value.find((t) => t.id === tag.id)
  if (!fullTag) return
  if (!selectedItems.value.some((item) => item.id === fullTag.id)) {
    selectedItems.value = [...selectedItems.value, fullTag]
  }
}

function getTagType(tag_type_id) {
  return tagTypes.value[tag_type_id] || {}
}

async function generateSuggestions() {
  suggestionsLoading.value = true

  try {
    if (!currentProject.value?.id) {
      console.error("No project ID available")
      suggestionsLoading.value = false
      return
    }

    const response = await TagApi.getRecommendations(currentProject.value.id)

    // Handle the new response structure with recommendations field
    const suggestions = response.data?.recommendations || response.recommendations || []

    // Ensure suggestions is an array
    if (Array.isArray(suggestions)) {
      tagSuggestions.value = suggestions
    } else {
      console.error("API response recommendations is not an array:", suggestions)
      tagSuggestions.value = []
    }

    suggestionsLoading.value = false
    suggestionsGenerated.value = true
    suggestionsExpanded.value = true
  } catch (error) {
    console.error("Error generating AI suggestions:", error)
    tagSuggestions.value = []
    suggestionsLoading.value = false
    // You might want to show an error message to the user here
  }
}
</script>

<style scoped src="@/styles/tagpicker.scss"></style>
<style scoped>
.mitre-suggestions-panel {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: padding 0.2s ease;
}
.mitre-suggestions-panel.collapsed {
  padding: 8px 16px;
}
.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.suggestion-title {
  font-weight: 400;
  font-size: 15px;
  color: #888;
}
.suggestion-title.clickable {
  cursor: pointer;
  transition: color 0.2s ease;
}
.suggestion-title.clickable:hover {
  color: #555;
}
.collapse-btn {
  color: #666 !important;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}
.collapse-btn:hover {
  opacity: 1;
}
.collapse-btn.v-btn {
  border: none !important;
  box-shadow: none !important;
}
.collapse-btn.v-btn .v-btn__overlay {
  display: none !important;
}

.suggestion-content {
  overflow: hidden;
}

.suggestion-collapse-enter-active,
.suggestion-collapse-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  opacity: 1;
}

.suggestion-collapse-enter-from,
.suggestion-collapse-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  margin-bottom: 0;
}
.suggestion-group-label {
  font-weight: 600;
  margin-right: 8px;
}
.suggestion-chip-wrapper {
  display: inline-block;
}
.suggestion-chip {
  margin-bottom: 4px;
  cursor: pointer;
}
.tactic-chip {
  background: #e3f2fd !important;
  color: #1a237e !important;
}
.technique-chip {
  background: #e8f5e9 !important;
  color: #1b5e20 !important;
}
.add-chip {
  margin-left: 4px;
  color: #388e3c;
}
.suggestion-help-text {
  font-size: 12px;
  color: #aaa;
  display: flex;
  align-items: center;
  margin-top: 8px;
}
.chip-group {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 0;
}
.tag-picker-row {
  display: flex;
  align-items: flex-start;
}
.tag-picker-outline {
  position: relative;
  flex: 1;
  border: 1.5px solid #cfd8dc;
  border-radius: 8px;
  padding: 12px 16px 8px 40px; /* left padding for icon */
  background: #fff;
  min-height: 56px;
  margin-bottom: 16px;
}
.tag-add-icon {
  position: absolute;
  left: 12px;
  top: 16px;
  z-index: 2;
}
.tag-copy-icon {
  margin-left: 12px;
  margin-top: 8px;
}
.tag-picker-label {
  position: absolute;
  top: -10px;
  left: 16px;
  background: #fff;
  padding: 0 4px;
  font-size: 13px;
  color: #757575;
  z-index: 1;
}
.tag-picker-dropdown,
.tag-picker-dropdown-wrapper {
  position: static !important;
  left: auto !important;
  right: auto !important;
  top: auto !important;
  z-index: auto !important;
  margin-top: 0 !important;
  max-height: none !important;
  overflow: visible !important;
  box-shadow: none !important;
  background: none !important;
}
.tag-picker-dropdown-block {
  margin-bottom: 16px;
}

.gradient-border-wrapper {
  position: relative;
  display: inline-block;
  border-radius: 24px;
  padding: 2px;
  background: linear-gradient(45deg, #00d4ff, #3b82f6, #8b5cf6, #ec4899, #00d4ff);
  background-size: 300% 300%;
  animation: gradientBorder 3s ease infinite;
}

@keyframes gradientBorder {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.generate-suggestions-btn {
  color: #1a1a1a !important;
  border: none !important;
  border-radius: 22px !important;
  background: #ffffff !important;
  --v-theme-surface: #ffffff !important;
  --v-theme-on-surface: #1a1a1a !important;
}

.generate-suggestions-btn .v-btn__content {
  color: #1a1a1a !important;
}

.generate-suggestions-btn.v-btn {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

.generate-suggestions-btn.v-btn .v-btn__underlay {
  background-color: #ffffff !important;
}

.generate-suggestions-btn.v-btn .v-btn__overlay {
  background: #ffffff !important;
  opacity: 0 !important;
}

.white-bg-wrapper {
  background: #ffffff;
  border-radius: 22px;
  overflow: hidden;
}

.gradient-border-wrapper .v-btn--variant-flat {
  background-color: #ffffff !important;
  background: #ffffff !important;
  border: none !important;
}

.generate-suggestions-btn .generate-btn-text {
  font-weight: normal;
  text-transform: none;
  color: #1a1a1a;
}

/* .tag-chip {
  font-size: 15px;
  padding: 0 12px;
  height: 32px;
} */
</style>
