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
    @update:search-input="getFilteredData()"
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
import { cloneDeep, debounce } from "lodash"

import SearchUtils from "@/search/utils"
import DefinitionApi from "@/definition/api"

export default {
  name: "DefinitionCombobox",
  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    project: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
    }
  },

  computed: {
    definitions: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._definitions = value.map((v) => {
          if (typeof v === "string") {
            v = {
              text: v,
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._definitions)
      },
    },
  },

  created() {
    this.fetchData()
  },

  methods: {
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        filters: {
          project: [this.project],
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      DefinitionApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
  },
}
</script>
