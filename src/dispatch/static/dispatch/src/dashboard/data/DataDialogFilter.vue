<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Dashboard Data Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="filters.project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" text @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
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
    ...mapFields("route", ["query"]),
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
    this.filters = { ...this.filters, ...RouterUtils.deserializeFilters(this.query) }
    this.fetchData()
  },
}
</script>
