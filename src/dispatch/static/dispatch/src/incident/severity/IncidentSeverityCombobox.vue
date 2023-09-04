<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    clearable
    closable-chips
    hide-selected
    item-title="id"
    multiple
    no-filter
    v-model="incidentSeverity"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No incident severities matching "
          <strong>{{ search }}</strong
          >".
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #selection="{ item, index }">
      <v-chip closable @click:close="remove(index)">
        <span v-if="!project"> {{ item.project.name }}/ </span>{{ item.name }}
      </v-chip>
    </template>
    <template #item="data">
      <v-list-item-title>
        <span v-if="!project">{{ data.item.project.name }}/</span>{{ data.item.name }}
      </v-list-item-title>
      <v-list-item-subtitle style="width: 200px" class="text-truncate">
        {{ data.item.description }}
      </v-list-item-subtitle>
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
import IncidentSeverityApi from "@/incident/severity/api"

export default {
  name: "IncidentSeverityComboBox",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: function () {
        return "Severities"
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
    incidentSeverity: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        const incidentSeverities = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", incidentSeverities)
      },
    },
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
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
      }

      let enabledFilter = [
        {
          model: "IncidentSeverity",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        enabledFilter
      )

      IncidentSeverityApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total
        this.loading = false

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
    remove(index) {
      const value = cloneDeep(this.value)
      value.splice(index, 1)
      this.$emit("input", value)
    },
  },

  created() {
    this.fetchData()
  },
}
</script>
