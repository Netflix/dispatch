<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    closable-chips
    item-title="name"
    item-value="id"
    hide-selected
    multiple
    no-filter
    v-model="tags"
    :menu-props="{ maxWidth: 0 }"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No tags matching "
          <strong>{{ search }}</strong
          >"
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #chip="{ item, props }">
      <v-chip v-bind="props">
        <span v-if="item.raw.tag_type">
          <span v-if="!project">{{ item.raw.project.name }}/</span>{{ item.raw.tag_type.name }}/
        </span>
        <a :href="item.raw.uri" target="_blank" :title="item.raw.description">
          {{ item.raw.name }}
        </a>
      </v-chip>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="null">
        <v-list-item-title>
          <span v-if="!project">{{ item.raw.project.name }}/</span>{{ item.raw.tag_type.name }}/{{
            item.raw.name
          }}
        </v-list-item-title>
        <v-list-item-subtitle :title="item.raw.description">
          {{ item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import SearchUtils from "@/search/utils"
import TagApi from "@/tag/api"

export default {
  name: "TagAutoComplete",

  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Add Tags",
    },
    model: {
      type: String,
      default: null,
    },
    modelId: {
      type: Number,
      default: null,
    },
    project: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      search: null,
    }
  },

  computed: {
    tags: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
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
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchData() {
      this.error = null
      this.loading = "error"

      // NOTE: Disabled until loading more is supported
      //
      // Fetch recommendations model and ID are provided
      // if (!this.search) {
      //   if (this.model && this.modelId) {
      //     TagApi.getRecommendations(this.model, this.modelId).then((response) => {
      //       this.items = response.data.items
      //       this.total = response.data.total
      //       // we don't support more for suggestions (limited)
      //       this.more = false
      //       this.loading = false
      //     })
      //     return
      //   }
      // }

      let filterOptions = {
        q: this.search,
        itemsPerPage: this.numItems,
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

        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>
