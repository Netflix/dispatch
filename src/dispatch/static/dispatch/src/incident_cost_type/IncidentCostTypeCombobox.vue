<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    deletable-chips
    hide-selected
    item-text="name"
    item-value="id"
    no-filter
    v-model="incident_cost_type"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No cost types matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title>
          <div>
            {{ data.item.name }}
          </div>
        </v-list-item-title>
        <v-list-item-subtitle>
          <div style="width: 200px" class="text-truncate">
            {{ data.item.description }}
          </div>
        </v-list-item-subtitle>
      </v-list-item-content>
    </template>
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
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
    value: {
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
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
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
