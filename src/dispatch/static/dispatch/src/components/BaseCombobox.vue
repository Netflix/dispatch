<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    chips
    clearable
    hide-selected
    :item-text="getItemName"
    item-value="id"
    multiple
    no-filter
    v-model="selectedItems"
  >
    <slot name="selection" v-bind="{ attr, item, selected }"></slot>
  </v-combobox>
</template>

<script>
import { debounce } from "lodash"

import SearchUtils from "@/search/utils"

export default {
  name: "BaseCombobox",

  props: {
    value: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: "Add Items",
    },
    api: {
      type: Object,
      required: true,
    },
    project: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      createdItem: null,
      search: null,
      attr: {},
      item: null,
      selected: null,
    }
  },

  computed: {
    selectedItems: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
      }
    )
  },

  watch: {
    createdItem: function (newVal) {
      this.items.push(newVal)
      this.selectedItems = [newVal]
    },
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    getItemName(item) {
      if (item === null) {
        return "Unknown"
      }
      return item.name
    },
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        itemsPerPage: this.numItems,
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

      this.api.getAll(filterOptions).then((response) => {
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
