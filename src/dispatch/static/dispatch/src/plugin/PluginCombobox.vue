<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    closable-chips
    hide-selected
    item-title="slug"
    no-filter
    v-model="plugin"
    clearable
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No Plugins matching "
          <strong>{{ search }}</strong
          >"
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>
          {{ data.item.raw.title }}
        </v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.description">
          {{ data.item.raw.description }}
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
import PluginApi from "@/plugin/api"

export default {
  name: "PluginCombobox",
  props: {
    modelValue: {
      type: [Object],
      default: null,
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
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        if (typeof value === "string") {
          let v = {
            slug: value,
          }
          this.items.push(v)
        }
        this.$emit("update:modelValue", value)
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
          plugin: [{ model: "Plugin", field: "type", value: this.type }],
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
