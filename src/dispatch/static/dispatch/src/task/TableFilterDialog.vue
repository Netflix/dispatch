<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Task Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <project-combobox v-model="local_project" label="Projects" />
        </v-list-item>
        <v-list-item>
          <incident-combobox v-model="local_incident" label="Incidents" />
        </v-list-item>
        <v-list-item>
          <incident-type-combobox v-model="local_incident_type" label="Incident Types" />
        </v-list-item>
        <v-list-item>
          <incident-priority-combobox
            v-model="local_incident_priority"
            label="Incident Priorities"
          />
        </v-list-item>
        <v-list-item>
          <task-status-multi-select v-model="local_status" label="Statuses" />
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
import { mapFields } from "vuex-map-fields"

import IncidentCombobox from "@/incident/IncidentFilterCombobox.vue"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TaskStatusMultiSelect from "@/task/TaskStatusMultiSelect.vue"

export default {
  name: "TaskTableFilterDialog",

  components: {
    IncidentCombobox,
    IncidentPriorityCombobox,
    IncidentTypeCombobox,
    ProjectCombobox,
    TaskStatusMultiSelect,
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
      local_project: this.projects,
      local_incident: [],
      local_incident_type: [],
      local_incident_priority: [],
      local_status: [],
    }
  },

  computed: {
    ...mapFields("task", [
      "table.options.filters.project",
      "table.options.filters.incident",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
    ]),
    numFilters: function () {
      return sum([
        this.project.length,
        this.incident.length,
        this.incident_type.length,
        this.incident_priority.length,
        this.status.length,
      ])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.project = this.local_project
      this.incident = this.local_incident
      this.incident_type = this.local_incident_type
      this.incident_priority = this.local_incident_priority
      this.status = this.local_status

      // we close the dialog
      this.display = false
    },
  },
}
</script>
