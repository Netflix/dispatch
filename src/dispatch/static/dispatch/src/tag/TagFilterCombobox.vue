<template>
  <v-combobox
    v-model="tags"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    hide-selected
    :label="label"
    multiple
    clearable
    chips
    :loading="loading"
    no-filter
    @update:search-input="getFilteredData()"
  >
    <template v-slot:no-data>
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
    <template v-slot:selection="data">
      <v-chip> {{ data.item.tag_type.name }}/{{ data.item.name }} </v-chip>
    </template>
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name" />
          <v-list-item-subtitle v-if="data.item.tag_type" v-text="data.item.tag_type.name" />
        </v-list-item-content>
      </template>
    </template>
    <template v-slot:append-item>
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
  name: "TagCombobox",
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
        this._tags = value.map((v) => {
          if (typeof v === "string") {
            v = {
              name: v,
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._tags)
      },
    },
  },

  created() {
    this.fetchData({})
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

      // fetch recommendations model and ID are provided
      if (!this.search) {
        if (this.model && this.modelId) {
          TagApi.getRecommendations(this.model, this.modelId).then((response) => {
            this.items = response.data.items
            this.total = response.data.total
            // we don't support more for suggestions (limited)
            this.more = false
            this.loading = false
          })
          return
        }
      }

      let filterOptions = {
        q: this.search,
        itemsPerPage: this.numItems,
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
      }

      let tagTypeFilter = {}
      if (filterOptions.q) {
        if (filterOptions.q.indexOf("/") != -1) {
          let [tagType, query] = filterOptions.q.split("/")
          filterOptions.q = query
          tagTypeFilter = [{ model: "TagType", field: "name", op: "==", value: tagType }]
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        tagTypeFilter
      )

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
