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
    v-model="caseSeverity"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No case severities matching "
          <strong>{{ search }}</strong
          >".
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #chip="{ item, props }">
      <v-chip v-bind="props">
        <span>{{ item.raw.project.name }}/</span>{{ item.raw.name }}
      </v-chip>
    </template>
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>
          <span>{{ data.item.raw.project.name }}/</span>{{ data.item.raw.name }}
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
import CaseSeverityApi from "@/case/severity/api"

export default {
  name: "CaseSeverityComboBox",

  props: {
    modelValue: {
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
    caseSeverity: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        const caseSeverities = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", caseSeverities)
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
        sortBy: ["project_id", "name"],
        descending: [false, false],
        itemsPerPage: this.numItems,
      }

      let enabledFilter = [
        {
          model: "CaseSeverity",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      if (this.project && this.project.length > 0) {
        const project_ids = this.project.map((p) => p.id)
        enabledFilter.push({
          model: "CaseSeverity",
          field: "project_id",
          op: "in",
          value: project_ids,
        })
      }

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        "CaseSeverity",
        enabledFilter
      )

      CaseSeverityApi.getAll(filterOptions).then((response) => {
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
}
</script>
