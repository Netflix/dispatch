<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    closable-chips
    hide-selected
    item-title="text"
    multiple
    no-filter
    v-model="terms"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No terms matching "
          <strong>{{ search }}</strong
          >". Press <kbd>enter</kbd> to create a new one.
        </v-list-item-title>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import SearchUtils from "@/search/utils"
import TermApi from "@/term/api"

export default {
  name: "TermCombobox",
  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Add Terms",
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
      search: null,
    }
  },

  computed: {
    terms: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        const terms = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", terms)
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
        itemsPerPage: this.numItems,
        filters: {
          project: [this.project],
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      TermApi.getAll(filterOptions).then((response) => {
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
}
</script>
