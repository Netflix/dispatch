<template>
  <v-combobox
    v-model="plugin_event"
    :loading="loading"
    :items="items"
    item-title="name"
    v-model:search="search"
    hide-selected
    :plugin="plugin"
    :label="label"
    no-filter
    clearable
    return-object
  >
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>
          {{ data.item.raw.name }}
        </v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.slug">
          {{ data.item.raw.slug }}
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
  name: "PluginEventCombobox",
  props: {
    modelValue: {
      type: [Object],
      default: null,
    },
    label: {
      type: String,
      default: "Plugin Events",
    },
    plugin: {
      type: [Object],
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
      plugin_event: null,
    }
  },

  created() {
    this.plugin_event = cloneDeep(this.modelValue)
    this.fetchData()
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchData() {
      if (!this.plugin) {
        return
      }
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
        filters: {
          plugin: [this.plugin.plugin],
        },
      }
      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      PluginApi.getAllPluginEvents(filterOptions).then((response) => {
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
  watch: {
    search(val) {
      val && val !== this.select && this.getFilteredData(val)
    },
    plugin(val) {
      this.plugin_event = null
      this.$emit("update:modelValue", null)
      val && this.getFilteredData(val)
    },
    plugin_event(val) {
      this.$emit("update:modelValue", val)
      this.getFilteredData(val)
    },
  },
}
</script>
