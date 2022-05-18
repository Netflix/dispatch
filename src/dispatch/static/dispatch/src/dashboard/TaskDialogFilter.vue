<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Dashboard Task Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <incident-window-input v-model="filters.created_at" label="Created At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="filters.project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="filters.incident_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="filters.incident_priority" />
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
import startOfMonth from "date-fns/startOfMonth"
import subMonths from "date-fns/subMonths"

import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentWindowInput from "@/incident/IncidentWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import RouterUtils from "@/router/utils"
import SearchUtils from "@/search/utils"
import TaskApi from "@/task/api"

let today = function () {
  let now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export default {
  name: "TaskOverviewFilterDialog",

  components: {
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    ProjectCombobox,
    IncidentWindowInput,
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
      filters: {
        project: this.projects,
        incident_type: [],
        incident_priority: [],
        status: [],
        tag: [],
        created_at: {
          start: null,
          end: null,
        },
      },
    }
  },

  computed: {
    numFilters: function () {
      return sum([
        this.filters.tag.length,
        this.filters.incident_priority.length,
        this.filters.incident_type.length,
        this.filters.status.length,
        this.filters.project.length,
        1,
      ])
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

      this.$emit("loading", "error")
      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)
      // this.$emit("filterOptions", filterOptions)
      TaskApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...{
        created_at: {
          start: startOfMonth(subMonths(today(), 1)).toISOString().slice(0, -1),
          end: today().toISOString().slice(0, -1),
        },
      },
      ...RouterUtils.deserializeFilters(this.query), // Order matters as values will overwrite
    }
    this.fetchData()
  },
}
</script>
