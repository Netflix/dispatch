<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    :menu-props="{ maxHeight: '400' }"
    deletable-chips
    hide-selected
    :placeholder="placeholder"
    :hint="hint"
    :item-text="itemText"
    no-filter
    v-model="value"
    clearable
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No {{ model }} matching " <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title>
          <div>
            {{ data.item.title }}
          </div>
        </v-list-item-title>
        <v-list-item-subtitle>
          <div style="width: 200px" class="text-truncate">
            {{ data.item.description }}
          </div>
        </v-list-item-subtitle>
      </v-list-item-content>
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
import PluginApi from "@/plugin/api"

export default {
  name: "Combobox",
  props: {
    value: {
      type: [Object],
      default: null,
    },
    type: {
      type: String,
      default: null,
    },
    label: {
      type: String,
    },
    numItems: {
      type: Int,
      default: 5,
    },
    sortBy: {
      type: String,
    },
    model: {
      type: String,
    },
    resource: {
      type: Object,
    },
    filters: {
      type: Object,
    },
    project: {
      type: [Object],
      default: null,
    },
  },
  data() {
    return {
      loading: false,
      items: [],
      more: false,
      search: null,
    }
  },

  computed: {
    item: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        if (typeof value === "string") {
          let v = {
            slug: value,
          }
          this.items.push(v)
        }
        this.$emit("input", value)
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

      let filterOptions = {
        q: this.search,
        sortBy: [this.sortBy],
        descending: [this.descending],
        itemsPerPage: this.numItems,
        filters: this.filters,
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
        filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      }

      this.resource.getAll(filterOptions).then((response) => {
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
