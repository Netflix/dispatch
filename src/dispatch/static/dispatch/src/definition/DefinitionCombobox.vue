<template>
  <v-combobox
    :items="items"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    closable-chips
    hide-selected
    label="Add definitions"
    multiple
    no-filter
    v-model="definitions"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No results matching "
          <strong>{{ search }}</strong
          >". Press <kbd>enter</kbd> to create a new one
        </v-list-item-title>
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
import DefinitionApi from "@/definition/api"

export default {
  name: "DefinitionCombobox",
  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
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
    }
  },

  computed: {
    definitions: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        const definitions = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", definitions)
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
        filters: {
          project: [this.project],
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      DefinitionApi.getAll(filterOptions).then((response) => {
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
}
</script>
