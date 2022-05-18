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
            <incident-window-input v-model="local_reported_at" label="Reported At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-window-input v-model="local_closed_at" label="Closed At" />
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

import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentWindowInput from "@/incident/IncidentWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "IncidentTableFilterDialog",

  components: {
    IncidentPriorityCombobox,
    IncidentStatusMultiSelect,
    IncidentTypeCombobox,
    IncidentWindowInput,
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
      local_reported_at: {},
      local_closed_at: {},
      local_project: this.projects,
      local_incident_type: [],
      local_incident_priority: [],
      local_status: [],
      local_tag_type: [],
      local_tag: [],
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.filters.reported_at",
      "table.options.filters.closed_at",
      "table.options.filters.project",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.options.filters.tag_type",
      "table.options.filters.tag",
    ]),
    numFilters: function () {
      return sum([
        this.incident_type.length,
        this.incident_priority.length,
        this.project.length,
        this.tag.length,
        this.tag_type.length,
        this.status.length,
      ])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.reported_at = this.local_reported_at
      this.closed_at = this.local_closed_at
      this.project = this.local_project
      this.incident_type = this.local_incident_type
      this.incident_priority = this.local_incident_priority
      this.status = this.local_status
      this.tag_type = this.local_tag_type
      this.tag = this.local_tag

      // we close the dialog
      this.display = false
    },
  },
}
</script>
