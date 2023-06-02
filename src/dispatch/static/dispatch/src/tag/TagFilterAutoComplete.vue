<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    chips
    clearable
    item-text="name"
    item-value="id"
    hide-selected
    multiple
    no-filter
    v-model="tags"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No tags matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:selection="{ item, index }">
      <v-chip close @click:close="value.splice(index, 1)">
        <span v-if="item.tag_type">
          <span v-if="!project">{{ item.project.name }}/</span>{{ item.tag_type.name }}/
        </span>
        <a :href="item.uri" target="_blank" :title="item.description">
          {{ item.name }}
        </a>
      </v-chip>
    </template>
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title>
          <span v-if="!project">{{ data.item.project.name }}/</span>{{ data.item.tag_type.name }}/{{
            data.item.name
          }}
        </v-list-item-title>
        <v-list-item-subtitle style="width: 200px" class="text-truncate">
          {{ data.item.description }}
        </v-list-item-subtitle>
      </v-list-item-content>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
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
    value: {
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
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._tags = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", this._tags)
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
