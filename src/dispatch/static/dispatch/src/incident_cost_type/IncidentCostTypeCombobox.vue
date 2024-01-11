<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    closable-chips
    hide-selected
    item-title="name"
    item-value="id"
    no-filter
    v-model="incident_cost_type"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No cost types matching "<strong>{{ search }}</strong
          >"
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

import IncidentCostTypeApi from "@/incident_cost_type/api"
import SearchUtils from "@/search/utils"

export default {
  name: "IncidentCostTypeCombobox",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: "Cost Type",
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
    incident_cost_type: {
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
        sortBy: ["category"],
        descending: [false],
        itemsPerPage: this.numItems,
        filters: {
          cost_type: [{ model: "IncidentCostType", field: "editable", op: "==", value: "true" }],
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      IncidentCostTypeApi.getAll(filterOptions).then((response) => {
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
