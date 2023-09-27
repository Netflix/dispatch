<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Dashboard Data Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <project-combobox v-model="filters.project" label="Projects" />
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" variant="text" @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"

import DataSourceApi from "@/data/source/api.js"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import RouterUtils from "@/router/utils"
import SearchUtils from "@/search/utils"

export default {
  name: "DataOverviewFilterDialog",

  components: {
    ProjectCombobox,
  },

  props: {
    projects: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  data() {
    return {
      menuStart: false,
      menuEnd: false,
      display: false,
      sources: [],
      filters: {
        project: this.projects,
      },
    }
  },

  computed: {
    numFilters: function () {
      return sum([this.filters.project.length])
    },
  },

  methods: {
    applyFilters() {
      RouterUtils.updateURLFilters(this.filters)
      this.fetchData()
      // we close the dialog
      this.display = false
    },
    fetchData() {
      let filterOptions = {
        itemsPerPage: -1,
        descending: [false],
        sortBy: ["created_at"],
        filters: { ...this.filters },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)

      this.$emit("loading", "error")
      this.$emit("filterOptions", filterOptions)
      DataSourceApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
  },

  created() {
    this.filters = { ...this.filters, ...RouterUtils.deserializeFilters(this.$route.query) }
    this.fetchData()
  },
}
</script>
