<template>
  <v-combobox
    v-model="incidents"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    hide-selected
    :label="label"
    multiple
    clearable
    chips
    no-filter
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Incidents matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name"></v-list-item-title>
          <v-list-item-subtitle v-text="data.item.title"></v-list-item-subtitle>
        </v-list-item-content>
      </template>
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
import IncidentApi from "@/incident/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "IncidentFilterCombobox",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    },
    label: {
      type: String,
      default: "Add Incidents"
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
    incidents: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._incidents = value.map(v => {
          if (typeof v === "string") {
            v = {
              name: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._incidents)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.getFilteredData({ q: this.search, itemsPerPage: this.numItems })
    },
    fetchData(filterOptions) {
      this.error = null
      this.loading = true
      IncidentApi.getAll(filterOptions).then(response => {
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
