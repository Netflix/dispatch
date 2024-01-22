<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    hide-selected
    item-title="name"
    item-value="id"
    no-filter
    clearable
    v-model="cost_model"
    :rules="[is_valid]"
  >
    <template #chip="data">
      <v-chip :value="data.selected">
        {{ data.item.raw.name }}
      </v-chip>
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
    <template #append>
      <DTooltip text="View cost model documentation" hotkeys="">
        <template #activator="{ tooltip }">
          <v-btn
            icon
            v-bind="tooltip"
            variant="text"
            href="https://netflix.github.io/dispatch/docs/administration/settings/cost_model"
            target="_blank"
          >
            <v-icon>mdi-information-outline</v-icon>
          </v-btn>
        </template>
      </DTooltip>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import CostModelApi from "@/cost_model/api"
import SearchUtils from "@/search/utils"

export default {
  name: "CostModelCombobox",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: "Cost Model",
    },
  },
  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      search: null,
      is_valid: (value) => {
        if (typeof value === "string") {
          return "Invalid cost model"
        }
        return true
      },
    }
  },

  computed: {
    cost_model: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
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
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
        filters: {
          project: [this.project],
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      CostModelApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total

        this.more = false
        if (this.items.length < this.total) {
          this.more = true
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
