<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Dashboard Incident Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="filters.reported_at" label="Reported At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="filters.closed_at" label="Closed At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="filters.project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-auto-complete v-model="filters.tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="filters.incident_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-severity-combobox v-model="filters.incident_severity" />
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
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"

import startOfMonth from "date-fns/startOfMonth"
import subMonths from "date-fns/subMonths"

import DateWindowInput from "@/components/DateWindowInput.vue"
import IncidentApi from "@/incident/api"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentSeverityCombobox from "@/incident/severity/IncidentSeverityCombobox.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import RouterUtils from "@/router/utils"
import SearchUtils from "@/search/utils"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

let today = function () {
  let now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export default {
  name: "IncidentOverviewFilterDialog",

  components: {
    DateWindowInput,
    IncidentPriorityCombobox,
    IncidentSeverityCombobox,
    IncidentTypeCombobox,
    ProjectCombobox,
    TagFilterAutoComplete,
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
        incident_priority: [],
        incident_severity: [],
        incident_type: [],
        project: this.projects,
        status: [],
        tag: [],
        reported_at: {
          start: null,
          end: null,
        },
        closed_at: {
          start: null,
          end: null,
        },
      },
    }
  },

  computed: {
    numFilters: function () {
      return sum([
        this.filters.incident_priority.length,
        this.filters.incident_severity.length,
        this.filters.incident_type.length,
        this.filters.project.length,
        this.filters.status.length,
        this.filters.tag.length,
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
        sortBy: ["reported_at"],
        filters: { ...this.filters },
        include: [
          "closed_at",
          "commanders_location",
          "created_at",
          "duplicates",
          "incident_priority",
          "incident_severity",
          "incident_type",
          "name",
          "participants_location",
          "participants_team",
          "project",
          "reported_at",
          "reporters_location",
          "stable_at",
          "status",
          "tags",
          "title",
          "total_cost",
        ],
      }

      this.$emit("loading", "error")
      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)
      IncidentApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...{
        reported_at: {
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
