<template>
  <v-combobox
    v-model="definitions"
    :items="items"
    :search-input.sync="search"
    hide-selected
    label="Add definitions"
    multiple
    chips
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No results matching "
            <strong>{{ search }}</strong
            >". Press <kbd>enter</kbd> to create a new one
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import DefinitionApi from "@/definition/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "DefinitionCombobox",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
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
    definitions: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._definitions = value.map(v => {
          if (typeof v === "string") {
            v = {
              text: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._definitions)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = true
      DefinitionApi.getAll(filterOptions).then(response => {
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
