<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-form @submit.prevent v-slot="{ isValid }">
      <v-card>
        <v-card-title>
          <span class="text-h5">Incident Filters</span>
        </v-card-title>
        <v-list density="compact">
          <v-list-item>
            <date-window-input v-model="local_reported_at" label="Reported At" />
          </v-list-item>
          <v-list-item>
            <date-window-input v-model="local_closed_at" label="Closed At" />
          </v-list-item>
          <v-list-item>
            <project-combobox v-model="local_project" label="Projects" />
          </v-list-item>
          <v-list-item>
            <incident-type-combobox v-model="local_incident_type" />
          </v-list-item>
          <v-list-item>
            <incident-severity-combobox v-model="local_incident_severity" />
          </v-list-item>
          <v-list-item>
            <incident-priority-combobox v-model="local_incident_priority" />
          </v-list-item>
          <v-list-item>
            <incident-status-multi-select v-model="local_status" />
          </v-list-item>
          <v-list-item>
            <tag-type-filter-combobox v-model="local_tag_type" label="Tag Types" />
          </v-list-item>
          <v-card variant="outlined" class="ml-4 mr-4 mb-4">
            <v-card-subtitle class="mt-2 mb-2">Has <b>all</b> of these tags</v-card-subtitle>
            <v-list-item>
              <tag-filter-auto-complete
                v-model="local_tag_all"
                label="Tags"
                model="incident"
                :project="local_project"
              />
            </v-list-item>
          </v-card>
          <v-card variant="outlined" class="ml-4 mr-4">
            <v-card-subtitle class="mt-2 mb-2">Has <b>any</b> of these tags</v-card-subtitle>
            <v-list-item>
              <tag-filter-auto-complete
                v-model="local_tag"
                label="Tags"
                model="incident"
                :project="local_project"
              />
            </v-list-item>
          </v-card>
          <v-list-item>
            <v-card class="mx-auto">
              <v-card-title>Incident Participant</v-card-title>
              <v-card-subtitle>Show only incidents with this participant</v-card-subtitle>
              <participant-select
                class="ml-10 mr-5"
                v-model="local_participant"
                label="Participant"
                hint="Show only incidents with this participant"
                :project="local_project"
                clearable
                :rules="[only_one]"
              />
              <v-checkbox
                class="ml-10 mr-5"
                v-model="local_participant_is_commander"
                label="And this participant is the Incident Commander"
                :disabled="local_participant == null"
              />
            </v-card>
          </v-list-item>
        </v-list>
        <v-card-actions>
          <v-spacer />
          <v-btn color="info" :disabled="!isValid.value" variant="text" @click="applyFilters()">
            Apply Filters
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
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
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"
import ParticipantSelect from "@/components/ParticipantSelect.vue"

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
    ParticipantSelect,
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
      local_tag_all: [],
      local_tag_type: [],
      local_participant_is_commander: false,
      local_participant: null,
      only_one: (value) => {
        if (value && value.length > 1) {
          return "Only one is allowed"
        }
        return true
      },
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
      "table.options.filters.tag_all",
      "table.options.filters.tag_type",
      "table.options.filters.commander",
      "table.options.filters.participant",
    ]),
    numFilters: function () {
      return sum([
        this.incident_priority.length,
        this.incident_severity.length,
        this.incident_type.length,
        this.project.length,
        this.status.length,
        this.tag.length,
        this.tag_all.length,
        this.tag_type.length,
        this.local_participant == null ? 0 : 1,
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
      this.tag_all = this.local_tag_all
      this.tag_type = this.local_tag_type
      if (Array.isArray(this.local_participant)) {
        this.local_participant = this.local_participant[0]
      }
      this.participant = this.local_participant
      if (this.local_participant_is_commander) {
        this.commander = this.local_participant
        this.participant = null
      } else {
        this.commander = null
        this.participant = this.local_participant
      }

      // we close the dialog
      this.display = false
    },
  },
}
</script>
