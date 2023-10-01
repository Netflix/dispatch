<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :menu-props="{ maxHeight: '400' }"
    v-model:search="search"
    @update:search="getFilteredData({ q: $event })"
    item-title="name"
    item-value="id"
    clearable
    v-model="source"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No sources matching
          <strong>"{{ search }}"</strong>
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>
          {{ data.item.raw.name }}
        </v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.description">
          {{ data.item.raw.description }}
        </v-list-item-subtitle>
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
import SourceApi from "@/data/source/api"

export default {
  name: "SourceSelect",
  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: "Source",
    },
    project: {
      type: Object,
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
    source: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        if (typeof value !== "string") {
          this.$emit("update:modelValue", value)
        }
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
        sortBy: ["name"],
        descending: [false],
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      SourceApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items

        if (this.source) {
          // check to see if the current selection is available in the list and if not we add it
          if (!this.items.find((match) => match.id === this.source.id)) {
            this.items = [this.source].concat(this.items)
          }
        }

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
