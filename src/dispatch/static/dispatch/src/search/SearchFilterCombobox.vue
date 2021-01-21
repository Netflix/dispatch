<template>
  <v-combobox
    v-model="terms"
    :items="items"
    :search-input.sync="search"
    hide-selected
    :label="label"
    multiple
    chips
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No filters matching "
            <strong>{{ search }}</strong
            >". Press <kbd>enter</kbd> to create a new one.
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
      default: "Select Search Filter"
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
        this._terms = value.map(v => {
          if (typeof v === "string") {
            v = {
              text: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._terms)
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
