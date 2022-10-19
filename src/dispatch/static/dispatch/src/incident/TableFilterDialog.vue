<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Incident Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="local_reported_at" label="Reported At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="local_closed_at" label="Closed At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="local_project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="local_incident_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-severity-combobox v-model="local_incident_severity" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="local_incident_priority" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-status-multi-select v-model="local_status" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-type-filter-combobox v-model="local_tag_type" label="Tag Types" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-auto-complete v-model="local_tag" label="Tags" />
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

import DateWindowInput from "@/components/DateWindowInput.vue"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentSeverityCombobox from "@/incident/severity/IncidentSeverityCombobox.vue"
import IncidentStatusMultiSelect from "@/incident/status/IncidentStatusMultiSelect.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "IncidentTableFilterDialog",

  components: {
    DateWindowInput,
    IncidentPriorityCombobox,
    IncidentSeverityCombobox,
    IncidentStatusMultiSelect,
    IncidentTypeCombobox,
    ProjectCombobox,
    TagFilterAutoComplete,
    TagTypeFilterCombobox,
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
      display: false,
      local_closed_at: {},
      local_incident_priority: [],
      local_incident_severity: [],
      local_incident_type: [],
      local_project: this.projects,
      local_reported_at: {},
      local_status: [],
      local_tag: [],
      local_tag_type: [],
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.filters.closed_at",
      "table.options.filters.incident_priority",
      "table.options.filters.incident_severity",
      "table.options.filters.incident_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
    ]),
    numFilters: function () {
      return sum([
        this.incident_priority.length,
        this.incident_severity.length,
        this.incident_type.length,
        this.project.length,
        this.status.length,
        this.tag.length,
        this.tag_type.length,
      ])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.closed_at = this.local_closed_at
      this.incident_priority = this.local_incident_priority
      this.incident_severity = this.local_incident_severity
      this.incident_type = this.local_incident_type
      this.project = this.local_project
      this.reported_at = this.local_reported_at
      this.status = this.local_status
      this.tag = this.local_tag
      this.tag_type = this.local_tag_type

      // we close the dialog
      this.display = false
    },
  },
}
</script>
