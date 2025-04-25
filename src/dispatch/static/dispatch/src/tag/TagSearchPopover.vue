<script setup lang="ts">
import { ref, watch, computed } from "vue"
import TagApi from "@/tag/api"
import TagTypeApi from "@/tag_type/api"
import { useSavingState } from "@/composables/useSavingState"
import { useStore } from "vuex"
import CaseApi from "@/case/api"
import { debounce } from "lodash"
// TODO(wshel) Add proper models with zod:
// import type { TagRead } from "@/tag/models"

const props = defineProps({
  caseTags: {
    type: Array,
    default: () => [],
  },
})

const store = useStore()
const { setSaving } = useSavingState()
const allTags = ref<any[]>([])
const groupedTags = ref<any[]>([])
const selectedTags = ref<any[]>([])
const menu = ref(false)
const searchQuery = ref("")
const loading = ref(false)
const fetchError = ref<string | null>(null)
const hasFetchedForCurrentProject = ref(false)
const currentProjectId = ref<number | null>(null)
const tagsHaveChanged = ref(false) // Track if changes occurred while menu was open

// Initialize selected tags based on props
watch(
  () => props.caseTags,
  (newTags) => {
    if (newTags) {
      selectedTags.value = [...newTags]
      tagsHaveChanged.value = false // Reset change flag when props update
    }
  },
  { immediate: true, deep: true }
)

// Function to group tags by type
const convertData = (data: any[]) => {
  if (!data) return []
  const groupedObject = data.reduce((r, a) => {
    if (!a.tag_type || a.tag_type.id === undefined || a.tag_type.id === null) {
      // console.warn("Tag missing tag_type or tag_type.id:", a) // Keep minimal logs
      return r
    }
    const typeId = a.tag_type.id
    if (!r[typeId]) {
      r[typeId] = {
        id: typeId,
        icon: a.tag_type.icon,
        label: a.tag_type.name,
        desc: a.tag_type.description,
        color: a.tag_type.color,
        isRequired: a.tag_type.required ?? false,
        isExclusive: a.tag_type.exclusive ?? false,
        menuItems: [],
      }
    }
    r[typeId].menuItems.push(a)
    return r
  }, {} as Record<number, any>)

  return Object.values(groupedObject)
    .sort((a, b) => a.label.localeCompare(b.label))
    .map((group) => {
      group.menuItems.sort((a, b) => a.name.localeCompare(b.name))
      return group
    })
}

// Fetch all relevant tags and group them
const fetchData = async (force = false) => {
  const caseDetails = store.state.case_management.selected
  const project = caseDetails?.project
  const projectId = project?.id

  if (hasFetchedForCurrentProject.value && projectId === currentProjectId.value && !force) {
    return
  }

  loading.value = true
  fetchError.value = null
  allTags.value = []
  groupedTags.value = []
  currentProjectId.value = projectId

  if (!project) {
    fetchError.value = "Cannot load tags: No project context available."
    loading.value = false
    hasFetchedForCurrentProject.value = false
    return
  }

  try {
    // Step 1: Fetch relevant TagType IDs
    const tagTypeFilterOptions = {
      filter: JSON.stringify([
        {
          and: [
            { model: "TagType", field: "discoverable_case", op: "==", value: "true" },
            { model: "TagType", field: "project_id", op: "==", value: project.id },
          ],
        },
      ]),
      itemsPerPage: -1,
      fields: JSON.stringify(["id"]),
    }

    const tagTypeResponse = await TagTypeApi.getAll(tagTypeFilterOptions)
    const relevantTagTypeIds = tagTypeResponse.data.items.map((tt: { id: number }) => tt.id)

    if (!relevantTagTypeIds.length) {
      loading.value = false
      hasFetchedForCurrentProject.value = true
      return
    }

    // Step 2: Fetch Tags
    const tagFilterOptions = {
      filter: JSON.stringify([
        {
          and: [
            { model: "Tag", field: "tag_type_id", op: "in", value: relevantTagTypeIds },
            { model: "Tag", field: "discoverable", op: "==", value: "true" },
          ],
        },
      ]),
      project: [project],
      itemsPerPage: -1,
      sortBy: JSON.stringify(["tag_type.name", "name"]),
      sortDesc: JSON.stringify([false, false]),
    }

    const tagResponse = await TagApi.getAll(tagFilterOptions)
    allTags.value = tagResponse.data.items
    groupedTags.value = convertData(allTags.value)
  } catch (error) {
    console.error("Error fetching tags or tag types:", error)
    fetchError.value = "Failed to load tags. Please try again."
    allTags.value = []
    groupedTags.value = []
    hasFetchedForCurrentProject.value = false
  } finally {
    loading.value = false
    if (!fetchError.value) {
      hasFetchedForCurrentProject.value = true
    }
  }
}

// Computed property for filtering based on search query
const filteredGroupedTags = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) {
    return groupedTags.value
  }

  return groupedTags.value.reduce((acc, group) => {
    const filteredItems = group.menuItems.filter((item: any) =>
      item.name.toLowerCase().includes(query)
    )

    if (filteredItems.length > 0) {
      acc.push({ ...group, menuItems: filteredItems })
    }
    return acc
  }, [] as any[])
})

// Debounced search function
const debouncedSearch = debounce((query: string) => {
  searchQuery.value = query
}, 300)

// Re-fetch if project changes
watch(
  () => store.state.case_management.selected?.project?.id,
  (newId, oldId) => {
    if (newId !== oldId) {
      hasFetchedForCurrentProject.value = false
      if (menu.value) {
        fetchData(true)
      }
    }
  }
)

// Handler for prefetching data on hover
const prefetchData = () => {
  const currentProjectInStore = store.state.case_management.selected?.project?.id
  if (!hasFetchedForCurrentProject.value || currentProjectId.value !== currentProjectInStore) {
    fetchData()
  }
}

// Fetch data when menu opens if not already fetched & Save on close
watch(menu, (isOpen, wasOpen) => {
  if (isOpen) {
    prefetchData()
  } else if (wasOpen && !isOpen && tagsHaveChanged.value) {
    // Save on close if changed
    saveTagChanges()
  }
})

const isTagSelected = (tag: any) => {
  return Array.isArray(selectedTags.value) && selectedTags.value.some((t) => t.id === tag.id)
}

// Only updates the local selectedTags ref and marks changes
const toggleTag = (tag: any) => {
  const isCurrentlySelected = isTagSelected(tag)
  const tagType = tag.tag_type

  let newSelectedTags = [...(selectedTags.value || [])]

  if (isCurrentlySelected) {
    newSelectedTags = newSelectedTags.filter((t) => t.id !== tag.id)
  } else {
    if (tagType?.exclusive) {
      newSelectedTags = newSelectedTags.filter((t) => t.tag_type?.id !== tagType.id)
    }
    newSelectedTags.push(tag)
  }

  const oldIds = (selectedTags.value || []).map((t) => t.id).sort()
  const newIds = newSelectedTags.map((t) => t.id).sort()
  if (JSON.stringify(oldIds) !== JSON.stringify(newIds)) {
    selectedTags.value = newSelectedTags
    tagsHaveChanged.value = true
  }
}

const saveTagChanges = async () => {
  if (!tagsHaveChanged.value) return

  const caseDetails = store.state.case_management.selected
  if (!caseDetails) {
    console.error("Cannot save tags: Case details not available.")
    tagsHaveChanged.value = false
    return
  }

  const updatedCaseDetails = {
    ...caseDetails,
    tags: [...(selectedTags.value || [])],
  }

  setSaving(true)
  try {
    await CaseApi.update(updatedCaseDetails.id, updatedCaseDetails)
    tagsHaveChanged.value = false // Reset flag on success
  } catch (e) {
    console.error("Failed to save tag changes", e)
    store.dispatch("notification_backend/addBeNotification", {
      text: "Failed to save tag changes. Please try again.",
      type: "error",
    })
    tagsHaveChanged.value = false // Reset flag even on error
  } finally {
    setSaving(false)
  }
}

// Method to remove a tag and immediately save
const removeTagAndSave = async (tag: any) => {
  toggleTag(tag) // Update local state first
  await saveTagChanges()
}

// Computed property to find missing required tag types
const missingRequiredTagTypes = computed(() => {
  if (!groupedTags.value || groupedTags.value.length === 0) return []

  const requiredGroups = groupedTags.value.filter((group) => group.isRequired)
  if (!requiredGroups.length) return []

  const selectedTypeIds = new Set((selectedTags.value || []).map((tag) => tag.tag_type?.id))

  return requiredGroups
    .filter((group) => !selectedTypeIds.has(group.id))
    .map((group) => group.label)
})

const getTagColor = (tag: any) => {
  return tag.tag_type?.color || "#1976D2"
}

const getTagIcon = (tag: any) => {
  if (tag.tag_type?.icon) {
    return `mdi-${tag.tag_type.icon}`
  }
  return null
}
</script>

<template>
  <div>
    <!-- Display selected tags and activator button -->
    <div id="tag-popover-anchor" class="d-flex flex-wrap gap-2 mb-2">
      <v-chip
        v-for="tag in selectedTags"
        :key="tag.id"
        variant="outlined"
        size="small"
        class="mr-1 linear-tag"
        closable
        :close-icon="'mdi-close'"
        @click:close="removeTagAndSave(tag)"
      >
        <template #prepend>
          <v-icon
            v-if="getTagIcon(tag)"
            :icon="getTagIcon(tag)"
            size="14"
            :color="getTagColor(tag)"
            class="mr-1"
          />
          <span v-else class="tag-dot" :style="`background-color: ${getTagColor(tag)}`" />
        </template>
        {{ tag.name }}
      </v-chip>

      <!-- Menu Component -->
      <v-menu
        v-model="menu"
        :close-on-content-click="false"
        location="start"
        :offset="[16, 24]"
        transition="false"
        :max-width="300"
        :min-width="300"
        attach="#tag-popover-anchor"
        eager
      >
        <template #activator="{ props: menuProps }">
          <v-btn
            icon="mdi-plus"
            variant="text"
            size="small"
            v-bind="menuProps"
            class="add-tag-button"
            @mouseenter="prefetchData"
          />
        </template>

        <!-- Menu Content -->
        <v-card width="300" class="rounded-lg">
          <v-text-field
            v-model="searchQuery"
            density="compact"
            variant="solo"
            single-line
            hide-details
            flat
            placeholder="Search tags..."
            prepend-inner-icon="mdi-magnify"
            :loading="loading && !hasFetchedForCurrentProject"
            @update:model-value="debouncedSearch"
          />

          <v-divider />

          <v-list density="compact" class="tag-list-container">
            <!-- Loading State -->
            <v-list-item v-if="loading && !hasFetchedForCurrentProject" disabled>
              <template #title>
                <span class="text-subtitle-2">Loading tags...</span>
              </template>
            </v-list-item>

            <!-- Fetch Error State -->
            <v-list-item v-else-if="fetchError">
              <template #prepend>
                <v-icon color="error" size="small">mdi-alert-circle-outline</v-icon>
              </template>
              <template #title>
                <span class="text-caption text-error ml-n2">{{ fetchError }}</span>
              </template>
            </v-list-item>

            <!-- Empty State -->
            <v-list-item
              v-else-if="!loading && !fetchError && !filteredGroupedTags.length && !searchQuery"
              disabled
            >
              <template #title>
                <span class="text-subtitle-2">No discoverable tags found.</span>
              </template>
            </v-list-item>
            <v-list-item
              v-else-if="!loading && !fetchError && !filteredGroupedTags.length && searchQuery"
              disabled
            >
              <template #title>
                <span class="text-subtitle-2">No tags matching '{{ searchQuery }}' found.</span>
              </template>
            </v-list-item>

            <!-- Grouped Tags List -->
            <template
              v-else-if="!loading && !fetchError"
              v-for="group in filteredGroupedTags"
              :key="group.id"
            >
              <v-list-subheader class="tag-group-header">
                <v-icon
                  v-if="group.icon"
                  :icon="`mdi-${group.icon}`"
                  size="16"
                  :color="group.color"
                  class="mr-1"
                />
                <span
                  v-else
                  class="tag-dot mr-2"
                  :style="`background-color: ${group.color || '#9E9E9E'}`"
                />
                {{ group.label }}
                <v-chip
                  v-if="group.isRequired"
                  size="x-small"
                  color="info"
                  variant="tonal"
                  class="ml-2"
                >
                  Required
                </v-chip>
                <v-chip
                  v-if="group.isExclusive"
                  size="x-small"
                  color="warning"
                  variant="tonal"
                  class="ml-1"
                >
                  Exclusive
                </v-chip>
              </v-list-subheader>

              <v-list-item
                v-for="tag in group.menuItems"
                :key="tag.id"
                @click="toggleTag(tag)"
                :active="isTagSelected(tag)"
                :class="{ 'selected-tag-item': isTagSelected(tag) }"
                density="compact"
              >
                <template #prepend>
                  <v-checkbox-btn
                    :model-value="isTagSelected(tag)"
                    :color="getTagColor(tag)"
                    density="compact"
                    hide-details
                  />
                </template>
                <template #title>
                  <div class="d-flex align-center">
                    <span class="tag-name">{{ tag.name }}</span>
                  </div>
                </template>
              </v-list-item>
              <v-divider v-if="group.menuItems.length" class="my-1" />
            </template>

            <!-- Required Tags Validation Message -->
            <v-list-item
              v-if="!loading && !fetchError && missingRequiredTagTypes.length"
              class="required-warning mt-2"
            >
              <template #prepend>
                <v-icon color="error" size="small">mdi-alert-circle-outline</v-icon>
              </template>
              <template #title>
                <span class="text-caption text-error">
                  Missing required tags from: {{ missingRequiredTagTypes.join(", ") }}
                </span>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </div>
  </div>
</template>

<style scoped>
.add-tag-button {
  border: 1px dashed rgba(0, 0, 0, 0.2);
  border-radius: 50%;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.gap-2 {
  gap: 8px;
}

.linear-tag {
  border-radius: 16px !important;
  background-color: transparent !important;
  border: 1px solid rgba(0, 0, 0, 0.12) !important;
  color: rgba(0, 0, 0, 0.87) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 0 8px !important;
}

.linear-tag:hover {
  background-color: rgba(0, 0, 0, 0.04) !important;
}

.tag-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
}

.selected-tag-item {
  background-color: rgba(0, 0, 0, 0.04);
}

.tag-name {
  font-size: 13px;
  font-weight: 500;
}

:deep(.v-list-item__prepend) {
  margin-right: 8px !important;
}

.tag-group-header {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  margin-top: 10px;
  padding-left: 16px;
  line-height: 1.4;
  height: auto !important;
  min-height: 32px;
  align-items: center;
}

.tag-group-header .v-chip {
  margin-top: -2px;
}

.required-warning .v-list-item__prepend {
  align-self: center;
  margin-right: 4px !important;
}

.required-warning .v-list-item-title {
  white-space: normal;
  line-height: 1.2;
}

:deep(.v-list-item--density-compact .v-list-item__prepend > .v-checkbox-btn) {
  margin-inline-start: -8px;
}

.tag-list-container {
  max-height: 300px;
  overflow-y: auto;
}
</style>
