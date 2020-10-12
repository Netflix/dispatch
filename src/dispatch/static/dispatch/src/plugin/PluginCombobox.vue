<template>
  <v-combobox
    v-model="plugin"
    :items="items"
    item-text="slug"
    :search-input.sync="search"
    hide-selected
    :label="label"
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
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
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle>
            Load More
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import PluginApi from "@/plugin/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "PluginCombobox",
  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    },
    type: {
      type: String
    },
    label: {
      type: String,
      defualt: "Plugins"
    }
  },
  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      search: null
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
            slug: value
          }
          this.items.push(v)
        }
        this.$emit("input", value)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.getFilteredData({
        q: this.search,
        itemsPerPage: this.numItems
      })
    },
    fetchData(filterOptions) {
      this.error = null
      this.loading = true

      if (this.type) {
        // Add type filtering
        Object.assign(filterOptions, {
          "field[]": "type",
          "op[]": "==",
          "value[]": this.type
        })
      }

      PluginApi.getAll(filterOptions).then(response => {
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
    getFilteredData: debounce(function(options) {
      this.fetchData(options)
    }, 500)
  }
}
</script>
