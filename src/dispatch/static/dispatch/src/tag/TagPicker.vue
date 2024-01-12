<template>
  <span v-click-outside="closeMenu"
    ><v-text-field
      readonly
      label="Tags"
      @click="toggleMenu"
      variant="outlined"
      v-model="dummyText"
      class="main-panel"
    >
      <v-icon slot="append-inner" class="panel-button">
        {{ menu ? "mdi-minus" : "mdi-plus" }}
      </v-icon>
      <div class="form-container mt-2">
        <div class="chip-group" v-show="selectedItems.length">
          <span v-for="(item, index) in selectedItems" :key="item">
            <v-chip
              label
              :key="index"
              :color="item.tag_type.color"
              closable
              class="tag-chip"
              @click:close="removeItem(item.id)"
            >
              <span class="mr-2">
                <v-icon
                  v-if="item.tag_type.icon"
                  :icon="'mdi-' + item.tag_type.icon"
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
                    <!-- <span v-show="group.isRequired" class="tag-group-rule">Required</span> -->
                    <span v-show="group.isExclusive" class="tag-group-rule">Exclusive</span>
                    <span class="tag-group-icon-down"><v-icon>mdi-chevron-down</v-icon></span>
                    <v-icon class="tag-group-icon-up">mdi-chevron-up</v-icon>
                  </span>

                  <span class="tag-group-desc" v-text="group.desc" />
                  <span
                    class="tag-group-rule-desc"
                    v-show="
                      group.isExclusive &&
                      this.selectedItems.some((item) => item.tag_type.id === group.id)
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
</template>

<script>
import SearchUtils from "@/search/utils"
import TagApi from "@/tag/api"
import { cloneDeep, debounce } from "lodash"

export default {
  data() {
    return {
      menu: false,
      dummyText: " ",
      items: [],
      total: 0,
      more: false,
      groups: [],
      searchQuery: "",
      filteredMenuItems: [],
      isDropdownOpen: false,
    }
  },
  props: {
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
  },
  directives: {
    // add directive to close dropdown when clicked outside
    ClickOutside: {
      bind: function (el, binding, vnode) {
        el.clickOutsideEvent = function (event) {
          if (el && !(el == event.target || el.contains(event.target))) {
            vnode.context[binding.expression](event)
          }
        }
        document.body.addEventListener("click", el.clickOutsideEvent, { passive: true })
      },
      unbind: function (el) {
        document.body.removeEventListener("click", el.clickOutsideEvent)
      },
    },
  },
  created() {
    this.fetchData()
  },
  computed: {
    selectedItems: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        const tags = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", tags)
      },
    },
  },
  methods: {
    closeMenu() {
      this.menu = false
    },
    toggleMenu() {
      this.menu = !this.menu
    },
    showDropdown(state) {
      this.isDropdownOpen = state
    },
    removeItem(index) {
      this.selectedItems = this.selectedItems.filter((item) => item.id !== index)
    },
    performSearch() {
      this.filteredMenuItems = []

      this.groups.forEach((group) => {
        const filteredItems = group.menuItems.filter((item) =>
          item.name.toLowerCase().includes(this.searchQuery.toLowerCase())
        )
        this.filteredMenuItems.push(...filteredItems)
      })
    },
    isItemDisabled(group, item) {
      const isItemSelectedInGroup = this.selectedItems.some(
        (selectedItem) => selectedItem.tag_type.id === group.id
      )
      return (
        isItemSelectedInGroup &&
        !this.selectedItems.some((selectedItem) => selectedItem.id === item.id)
      )
    },
    getColorAsStyle(color) {
      return `color: '${color}'`
    },
    getBackgroundColorAsStyle(color) {
      return `background-color: '${color}'`
    },
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    convertTagsToItems(tags) {
      return tags.map((tag) => {
        return {
          ...tag,
          color: tag.tag_type.color,
          icon: tag.tag_type.icon,
        }
      })
    },
    convertData(data) {
      var groupedObject = data.reduce(function (r, a) {
        if (!r[a.tag_type.id]) {
          r[a.tag_type.id] = {
            id: a.tag_type.id,
            icon: a.tag_type.icon,
            label: a.tag_type.name,
            desc: a.tag_type.description,
            color: a.tag_type.color,
            // isRequired: a.tag_type.required,
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
    },
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        itemsPerPage: 100, //this.numItems,
        sortBy: ["tag_type.name"],
        descending: [false],
      }

      let filters = {}

      if (this.project) {
        filters["project"] = [this.project]
      }

      // add a filter to only retrun discoverable tags
      filters["tagFilter"] = [{ model: "Tag", field: "discoverable", op: "==", value: "true" }]

      if (filterOptions.q && filterOptions.q.indexOf("/") != -1) {
        // modify the query and add a tag type filter
        let [tagType, query] = filterOptions.q.split("/")
        filterOptions.q = query
        filters["tagTypeFilter"] = [
          { model: "TagType", field: "name", op: "==", value: tagType },
          { model: "TagType", field: "discoverable_" + this.model, op: "==", value: "true" },
        ]
      } else {
        filters["tagTypeFilter"] = [
          { model: "TagType", field: "discoverable_" + this.model, op: "==", value: "true" },
        ]
      }

      filterOptions = {
        ...filterOptions,
        filters: filters,
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      TagApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }
        this.groups = this.convertData(this.items)
        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>

<style scoped src="@/styles/tagpicker.scss"></style>
