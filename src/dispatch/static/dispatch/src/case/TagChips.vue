<template>
  <v-chip-group active-class="primary--text" column>
    <v-chip flat close small v-for="tag in _case.tags" :key="tag" @click:close="removeTag(tag)">
      {{ tag }}
    </v-chip>
    <v-chip flat small @click="toggleTagInput">
      <span v-if="!isAddingTag">Add tag <v-icon class="ml-1" small>mdi-plus</v-icon></span>
      <span v-else>Close <v-icon class="ml-1" small>mdi-close</v-icon></span>
    </v-chip>
    <v-autocomplete
      v-if="isAddingTag"
      v-model="selectedTag"
      :items="availableTags"
      item-text="name"
      item-value="name"
      prepend-inner-icon="search"
      return-object
      clearable
      dense
      small
      rounded
      solo
      @change="addTag"
      placeholder="Search tags..."
      cache-items="true"
      class="autocomplete-menu pt-2 mx-2"
      style="max-width: 250px"
    >
    </v-autocomplete>
  </v-chip-group>
</template>

<!-- ... Rest of your component -->

<script>
import { cloneDeep, debounce } from "lodash"

import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SearchUtils from "@/search/utils"
import TagApi from "@/tag/api"

export default {
  name: "TagChips",

  props: {
    _case: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      selectedTag: null,
      availableTags: [], // Fetch available tags from your API.
      isAddingTag: false,
    }
  },
  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
      }
    )
  },

  methods: {
    ...mapActions("case_management", ["save_page"]),
    toggleTagInput() {
      this.isAddingTag = !this.isAddingTag
      if (!this.isAddingTag) {
        this.selectedTag = null
      }
    },
    addTag() {
      if (this.selectedTag && !this._case.tags.includes(this.selectedTag.name)) {
        this._case.tags.push(this.selectedTag.name)

        // Remove the added tag from availableTags
        this.availableTags = this.availableTags.filter((tag) => tag.name !== this.selectedTag.name)

        this.selectedTag = null
        this.isAddingTag = false
        this.save_page(this._case)
      }
    },
    removeTag(tag) {
      const index = this._case.tags.indexOf(tag)
      if (index !== -1) {
        this._case.tags.splice(index, 1)

        // Add the removed tag back to availableTags
        const removedTag = this.items.find((item) => item.name === tag)
        if (removedTag) {
          this.availableTags.push(removedTag)
        }

        this.save_page(this._case)
      }
    },
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        itemsPerPage: -1,
        sortBy: ["tag_type.name"],
        descending: [false],
      }

      let filters = {}

      if (this.project) {
        // we add a project filter
        filters["project"] = [this.project]
      }

      // we add a filter to only retrun discoverable tags
      filters["tagFilter"] = [{ model: "Tag", field: "discoverable", op: "==", value: "true" }]

      if (filterOptions.q) {
        if (filterOptions.q.indexOf("/") != -1) {
          // we modify the query and add a tag type filter
          let [tagType, query] = filterOptions.q.split("/")
          filterOptions.q = query
          filters["tagTypeFilter"] = [{ model: "TagType", field: "name", op: "==", value: tagType }]
        }
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

        // Here, we filter the availableTags to only include those not already in _case.tags
        this.availableTags = response.data.items.filter(
          (item) => !this._case.tags.includes(item.name)
        )
        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>

<style scoped>
.autocomplete-menu .v-input__slot {
  position: relative;
}

.autocomplete-menu .v-autocomplete__content {
  position: absolute;
  width: 100%;
  box-shadow: 0px 8px 10px -5px rgba(0, 0, 0, 0.2), 0px 16px 24px 2px rgba(0, 0, 0, 0.14),
    0px 6px 30px 5px rgba(0, 0, 0, 0.12);
  border-radius: 4px;
}
</style>
