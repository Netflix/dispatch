<template>
  <v-autocomplete
    v-model="plugin"
    :loading="loading"
    :items="items"
    item-title="plugin.slug"
    item-value="plugin.slug"
    @update:search="getFilteredData()"
    v-model:search="search"
    hide-selected
    :label="label"
    no-filter
    return-object
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
          {{ data.item.raw.plugin.title }}
        </v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.plugin.description">
          {{ data.item.raw.plugin.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import SearchUtils from "@/search/utils"
import PluginApi from "@/plugin/api"

export default {
  name: "PluginCombobox",
  props: {
    modelValue: {
      type: Object,
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
    requiresPluginEvents: {
      type: Boolean,
      default: false,
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
    if (this.modelValue && this.modelValue.slug) {
      this.plugin = cloneDeep(this.modelValue)
    }
    this.fetchData()
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    async fetchData() {
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

      // Only display plugins that have PluginEvents.
      if (this.requiresPluginEvents) {
        await PluginApi.getAllPluginEvents().then((response) => {
          let plugin_events = response.data.items

          filter["and"].push({
            model: "Plugin",
            field: "slug",
            op: "in",
            value: plugin_events.map((p) => p.plugin.slug),
          })
        })
      }

      let filterOptions = {
        q: this.search,
        sortBy: ["Plugin.slug"],
        itemsPerPage: this.numItems,
        filter: JSON.stringify(filter),
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
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },

  watch: {
    search(val) {
      val && val !== this.select && this.getFilteredData(val)
    },
    plugin(val) {
      this.$emit("update:modelValue", val)
    },
  },
}
</script>
