<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Column Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <incident-combobox v-model="incident" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <task-status-multi-select v-model="status" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="incident_type" label="Incident Type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="incident_priority" label="Incident Priority" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
import IncidentCombobox from "@/incident/IncidentCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TaskStatusMultiSelect from "@/task/TaskStatusMultiSelect.vue"
export default {
  name: "TaskTableFilterDialog",
  components: {
    IncidentCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    ProjectCombobox,
    TaskStatusMultiSelect,
  },
  data() {
    return {
      display: false,
    }
  },
  computed: {
    ...mapFields("task", [
      "table.options.filters.creator",
      "table.options.filters.assignee",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.options.filters.project",
      "table.options.filters.incident",
    ]),
    numFilters: function () {
      return sum([
        this.creator.length,
        this.assignee.length,
        this.incident_type.length,
        this.incident.length,
        this.project.length,
        this.incident_priority.length,
        this.status.length,
      ])
    },
  },
}
</script>
