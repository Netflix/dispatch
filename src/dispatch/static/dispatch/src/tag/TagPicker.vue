<template>
  <span v-click-outside="closeMenu"
    ><v-text-field
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
    <v-card v-if="menu">
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
  </span>
  <v-snackbar v-model="snackbar" :timeout="2400" color="success">
    <v-row class="fill-height" align="center">
      <v-col class="text-center">Tags copied to the clipboard</v-col>
    </v-row>
  </v-snackbar>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { cloneDeep } from "lodash"
import SearchUtils from "@/search/utils"
import TagApi from "@/tag/api"

const ALL_DISCOVERABILITY_TYPES = [
  { model: "TagType", field: "discoverable_incident", op: "==", value: "true" },
  { model: "TagType", field: "discoverable_case", op: "==", value: "true" },
  { model: "TagType", field: "discoverable_signal", op: "==", value: "true" },
  { model: "TagType", field: "discoverable_query", op: "==", value: "true" },
  { model: "TagType", field: "discoverable_source", op: "==", value: "true" },
]

const menu = ref(false)
const dummyText = ref(" ")
const items = ref([])
const total = ref(0)
const more = ref(false)
const groups = ref([])
const searchQuery = ref("")
const filteredMenuItems = ref([])
const isDropdownOpen = ref(false)
const loading = ref(true)
const error = ref(true)
const snackbar = ref(false)

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

watch(
  () => props.project,
  () => {
    fetchData()
    validateTags(selectedItems.value)
  }
)
const check_for_error = () => {
  return error.value
}

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

const fetchData = () => {
  loading.value = true

  let filterOptions = {
    q: null,
    itemsPerPage: 100,
    sortBy: ["tag_type.name"],
    descending: [false],
  }

  let filters = {}

  if (props.project) {
    if (Array.isArray(props.project)) {
      if (props.project.length > 0) {
        filters["project"] = props.project
      }
    } else {
      filters["project"] = [props.project]
    }
    validateTags(selectedItems.value)
  }

  // add a filter to only retrun discoverable tags
  filters["tagFilter"] = [{ model: "Tag", field: "discoverable", op: "==", value: "true" }]

  if (filterOptions.q && filterOptions.q.indexOf("/") != -1) {
    // modify the query and add a tag type filter
    let [tagType, query] = filterOptions.q.split("/")
    filterOptions.q = query
    if (props.model) {
      filters["tagTypeFilter"] = [
        { model: "TagType", field: "name", op: "==", value: tagType },
        { model: "TagType", field: "discoverable_" + props.model, op: "==", value: "true" },
      ]
    } else {
      filters["tagTypeFilter"] = [
        { model: "TagType", field: "name", op: "==", value: tagType },
        ...ALL_DISCOVERABILITY_TYPES,
      ]
    }
  } else {
    if (props.model) {
      filters["tagTypeFilter"] = [
        { model: "TagType", field: "discoverable_" + props.model, op: "==", value: "true" },
      ]
    } else {
      filters["tagTypeFilter"] = ALL_DISCOVERABILITY_TYPES
    }
  }

  filterOptions = {
    ...filterOptions,
    filters: filters,
  }

  filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

  TagApi.getAll(filterOptions).then((response) => {
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
}

onMounted(fetchData)

const emit = defineEmits(["update:modelValue"])

function validateTags(value) {
  const project_id = props.project?.id || 0
  var all_tags_in_project = false
  if (project_id) {
    all_tags_in_project = value.every((tag) => tag.project?.id == project_id)
  } else {
    const project_name = props.project?.name
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

const getColorAsStyle = (color) => {
  return `color: '${color}'`
}

const getBackgroundColorAsStyle = (color) => {
  return `background-color: '${color}'`
}

const convertData = (data) => {
  var groupedObject = data.reduce(function (r, a) {
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
</script>

<style scoped src="@/styles/tagpicker.scss"></style>
