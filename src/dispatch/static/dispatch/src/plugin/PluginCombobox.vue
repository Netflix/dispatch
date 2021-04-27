<template>
  <v-combobox
    v-model="plugin"
    :items="items"
    item-text="slug"
    :search-input.sync="search"
    hide-selected
    :label="label"
    no-filter
    :loading="loading"
    @update:search-input="getFilteredData()"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Plugins matching "
            <strong>{{ search }}</strong
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
  name: "PluginCombobox",
  props: {
    value: {
      type: [Object, String],
      default: function () {
        return null
      },
    },
    type: {
      type: String,
      default: null,
    },
    label: {
      type: String,
      default: "Plugins",
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
    plugin: {
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
        sortBy: ["slug"],
        descending: [false],
        itemsPerPage: this.numItems,
        filters: {
          type: [this.type],
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      PluginApi.getAll(filterOptions).then((response) => {
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
