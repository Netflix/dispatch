<template>
  <v-dialog v-model="display" max-width="600">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Dashboard Incident Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <date-window-input v-model="filters.reported_at" label="Reported At" />
        </v-list-item>
        <v-list-item>
          <date-window-input v-model="filters.closed_at" label="Closed At" />
        </v-list-item>
        <v-list-item>
          <project-combobox v-model="filters.project" label="Projects" />
        </v-list-item>
        <v-list-item>
          <tag-filter-auto-complete
            v-model="filters.tag"
            label="Tags"
            model="incident"
            :project="filters.project"
          />
        </v-list-item>
        <v-list-item>
          <incident-type-combobox v-model="filters.incident_type" />
        </v-list-item>
        <v-list-item>
          <incident-severity-combobox v-model="filters.incident_severity" />
        </v-list-item>
        <v-list-item>
          <incident-priority-combobox v-model="filters.incident_priority" />
        </v-list-item>
        <v-list-item>
          <v-card class="mx-auto">
            <v-card-title>Incident Participant</v-card-title>
            <v-card-subtitle>Show only incidents with this participant</v-card-subtitle>
            <participant-select
              class="ml-10 mr-5"
              v-model="local_participant"
              label="Participant"
              hint="Show only incidents with this participant"
              :project="filters.project"
              clearable
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
        <v-btn color="info" variant="text" @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"

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
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import ParticipantSelect from "@/components/ParticipantSelect.vue"

let today = function () {
  let now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export default {
  name: "IncidentDialogFilter",

  components: {
    DateWindowInput,
    IncidentPriorityCombobox,
    IncidentSeverityCombobox,
    IncidentTypeCombobox,
    ProjectCombobox,
    TagFilterAutoComplete,
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
      local_participant_is_commander: false,
      local_participant: null,
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
        this.local_participant == null ? 0 : 1,
        1,
      ])
    },
  },

  methods: {
    applyFilters() {
      if (this.local_participant) {
        if (Array.isArray(this.local_participant)) {
          this.local_participant = this.local_participant[0]
        }
        if (this.local_participant_is_commander) {
          this.filters.commander = this.local_participant
          this.filters.participant = null
        } else {
          this.filters.commander = null
          this.filters.participant = this.local_participant
        }
      }
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
      ...RouterUtils.deserializeFilters(this.$route.query), // Order matters as values will overwrite
    }
    this.fetchData()
  },
}
</script>
