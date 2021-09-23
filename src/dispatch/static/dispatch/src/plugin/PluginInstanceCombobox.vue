<template>
  <v-autocomplete
    v-model="plugin"
    :loading="loading"
    :items="items"
    item-text="plugin.slug"
    :search-input.sync="search"
    hide-selected
    :label="label"
    no-filter
    return-object
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
            {{ data.item.plugin.title }}
          </div>
        </v-list-item-title>
        <v-list-item-subtitle>
          <div style="width: 200px" class="text-truncate">
            {{ data.item.plugin.description }}
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
  </v-autocomplete>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import PluginApi from "@/plugin/api"

export default {
  name: "PluginCombobox",
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
      default: "Plugins",
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
      numItems: 5,
      search: null,
      plugin: null,
    }
  },

  created() {
    this.plugin = cloneDeep(this.value)
    this.fetchData()
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
    },
    fetchData() {
      this.error = null
      this.loading = "error"
      let filter = {
        and: [
          {
            model: "PluginInstance",
            field: "enabled",
            op: "==",
            value: "true",
          },
          {
            model: "Project",
            field: "name",
            op: "==",
            value: this.project.name,
          },
        ],
      }

      if (this.type) {
        filter["and"].push({
          model: "Plugin",
          field: "type",
          op: "==",
          value: this.type,
        })
      }

      let filterOptions = {
        q: this.search,
        sortBy: ["slug"],
        itemsPerPage: this.numItems,
        filter: JSON.stringify(this.filter),
      }

      PluginApi.getAllInstances(filterOptions).then((response) => {
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
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
  },

  watch: {
    search(val) {
      val && val !== this.select && this.getFilteredData(val)
    },
    plugin(val) {
      this.$emit("input", val)
    },
  },
}
</script>
