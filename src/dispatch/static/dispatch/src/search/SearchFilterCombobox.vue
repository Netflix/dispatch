<template>
  <v-combobox
    v-model="terms"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    hide-selected
    :label="label"
    chips
    close
    clearable
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
  >
    <template v-slot:selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.name"></span>
      </v-chip>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item-content>
        <v-list-item-title v-text="item.name"></v-list-item-title>
        <v-list-item-subtitle v-text="item.description"></v-list-item-subtitle>
      </v-list-item-content>
    </template>
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No filters matching "
            <strong>{{ search }}</strong>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import SearchApi from "@/search/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "SearchFilterCombobox",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    },
    label: {
      type: String,
      default: "Search Filter"
    }
  },
  data() {
    return {
      loading: false,
      items: [],
      search: null
    }
  },

  computed: {
    terms: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._filters = value.map(v => {
          if (typeof v === "string") {
            v = {
              text: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._filters)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = "error"
      SearchApi.getAllFilters(filterOptions).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function(options) {
      this.fetchData(options)
    }, 500)
  }
}
</script>
