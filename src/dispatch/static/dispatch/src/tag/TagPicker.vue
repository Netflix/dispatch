<template>
  <div>
    <div v-click-outside="closeMenu">
      <span class="tag-picker-row">
        <div class="tag-picker-outline">
          <v-icon
            class="panel-button tag-add-icon"
            @click.stop="toggleMenu"
            style="cursor: pointer"
            >{{ menu ? "mdi-minus" : "mdi-plus" }}</v-icon
          >
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
        <div v-if="!suggestionsGenerated && props.visibility !== 'Restricted'" class="mb-4">
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
        <div v-if="suggestionsGenerated && suggestionsError" class="error-banner mb-3">
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
import { useStore } from "vuex"

const store = useStore()
const menu = ref(false)
const searchQuery = ref("")
const filteredMenuItems = ref([])
const isDropdownOpen = ref(false)
const snackbar = ref(false)
const suggestionsExpanded = ref(false)

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
    store.dispatch("tag/validateTags", {
      value: tags,
      groups: groups.value,
      currentProject: props.project,
    })
  },
})

const emit = defineEmits(["update:modelValue"])

// Methods
const fetchData = async () => {
  if (!props.project) return
  await store.dispatch("tag/fetchTags", {
    project: props.project,
    model: props.model,
  })
}

const fetchTagTypes = async () => {
  await store.dispatch("tag/fetchTagTypes")
}

const generateSuggestions = async () => {
  if (!props.project?.id) return
  await store.dispatch("tag/generateSuggestions", {
    projectId: props.project.id,
    modelId: props.modelId,
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
})

watch(
  () => props.project,
  (newVal) => {
    if (newVal) {
      fetchData()
    }
  }
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
