<script setup lang="ts">
import { ref, watch, onMounted } from "vue"
import TagApi from "@/tag/api"
import { useSavingState } from "@/composables/useSavingState"
import { useStore } from "vuex"
import CaseApi from "@/case/api"
import { debounce } from "lodash"

const props = defineProps({
  caseTags: {
    type: Array,
    default: () => [],
  },
})

const store = useStore()
const { setSaving } = useSavingState()
const tags = ref([])
const selectedTags = ref([])
const menu = ref(false)
const searchQuery = ref("")
const loading = ref(false)

// Initialize selected tags based on props
watch(
  () => props.caseTags,
  (newTags) => {
    if (newTags) {
      selectedTags.value = [...newTags]
    }
  },
  { immediate: true }
)

// Search for tags with debounce
const searchTags = debounce(async (query = "") => {
  loading.value = true
  try {
    const options = {
      filter: JSON.stringify([
        { and: [{ model: "Tag", field: "name", op: "ilike", value: `%${query}%` }] },
      ]),
      itemsPerPage: 10,
    }
    const response = await TagApi.getAll(options)
    tags.value = response.data.items

    // Check if we need to create default tags
    if (tags.value.length === 0 && !query) {
      createDefaultTags()
    }
  } catch (error) {
    console.error("Error searching tags:", error)
  } finally {
    loading.value = false
  }
}, 300)

// Create default tags if none exist
const createDefaultTags = async () => {
  const defaultTags = [
    { name: "Improvement", description: "An improvement to existing functionality" },
    { name: "Bug", description: "A bug or issue that needs fixing" },
    { name: "Feature", description: "A new feature or functionality" },
  ]

  for (const tag of defaultTags) {
    try {
      const response = await TagApi.create(tag)
      tags.value.push(response.data)
    } catch (error) {
      console.error(`Error creating tag ${tag.name}:`, error)
    }
  }
}

// Watch for search query changes
watch(searchQuery, (newQuery) => {
  searchTags(newQuery)
})

// Initial search on mount
onMounted(() => {
  searchTags("")
})

const isTagSelected = (tag) => {
  return selectedTags.value.some((t) => t.id === tag.id)
}

const toggleTag = async (tag) => {
  const caseDetails = store.state.case_management.selected

  if (isTagSelected(tag)) {
    // Remove tag
    selectedTags.value = selectedTags.value.filter((t) => t.id !== tag.id)
    caseDetails.tags = caseDetails.tags.filter((t) => t.id !== tag.id)
  } else {
    // Add tag
    selectedTags.value.push(tag)
    if (!caseDetails.tags) {
      caseDetails.tags = []
    }
    caseDetails.tags.push(tag)
  }

  // Update the case
  setSaving(true)
  try {
    await CaseApi.update(caseDetails.id, caseDetails)
    console.log("Case tags updated successfully")
  } catch (e) {
    console.error("Failed to update case tags", e)
  }
  setSaving(false)
}

const getTagColor = (tag) => {
  return tag.tag_type?.color || "#1976D2" // Default to blue if no color is specified
}

const getTagIcon = (tag) => {
  if (tag.tag_type?.icon) {
    return `mdi-${tag.tag_type.icon}`
  }
  return null
}
</script>

<template>
  <div>
    <!-- Display selected tags -->
    <div class="d-flex flex-wrap gap-2 mb-2">
      <v-chip
        v-for="tag in selectedTags"
        :key="tag.id"
        variant="outlined"
        size="small"
        class="mr-1 linear-tag"
        @click="toggleTag(tag)"
        closable
        :close-icon="'mdi-close'"
        @click:close="toggleTag(tag)"
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

      <v-menu
        v-model="menu"
        :close-on-content-click="false"
        location="start"
        :offset="[-420, 0]"
        transition="false"
        :max-width="300"
        :min-width="300"
        attach="body"
        eager
      >
        <template #activator="{ props: menuProps }">
          <v-btn
            icon="mdi-plus"
            variant="text"
            size="small"
            v-bind="menuProps"
            class="add-tag-button"
          />
        </template>

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
            :loading="loading"
          />

          <v-divider />

          <v-list density="compact">
            <v-list-item v-if="loading && tags.length === 0" disabled>
              <template #title>
                <span class="text-subtitle-2">Searching...</span>
              </template>
            </v-list-item>
            <v-list-item v-else-if="tags.length === 0" disabled>
              <template #title>
                <span class="text-subtitle-2">No matching tags found</span>
              </template>
            </v-list-item>
            <v-list-item
              v-for="tag in tags"
              :key="tag.id"
              @click="toggleTag(tag)"
              :active="isTagSelected(tag)"
              :class="{ 'selected-tag-item': isTagSelected(tag) }"
              density="compact"
            >
              <template #prepend>
                <v-checkbox
                  :model-value="isTagSelected(tag)"
                  :color="getTagColor(tag)"
                  density="compact"
                  hide-details
                />
              </template>
              <template #title>
                <div class="d-flex align-center">
                  <v-icon
                    v-if="getTagIcon(tag)"
                    :icon="getTagIcon(tag)"
                    size="14"
                    :color="getTagColor(tag)"
                    class="mr-1"
                  />
                  <span
                    v-else
                    class="tag-dot mr-2"
                    :style="`background-color: ${getTagColor(tag)}`"
                  />
                  <span class="tag-name">{{ tag.name }}</span>
                </div>
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

/* Override v-list-item styles for better spacing */
:deep(.v-list-item__prepend) {
  margin-right: 8px !important;
}
</style>
