<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="title"
          label="Title"
          hint="Title of the incident."
          clearable
          required
          name="Title"
          :rules="[rules.required]"
        />
      </v-col>
      <v-col cols="12">
        <v-textarea
          v-model="description"
          label="Description"
          hint="Description of the incident."
          clearable
          required
          name="Description"
          :rules="[rules.required]"
        />
      </v-col>
      <v-col cols="12">
        <v-textarea
          v-model="resolution"
          label="Resolution"
          hint="Description of the actions taken to resolve the incident."
          clearable
        />
      </v-col>
      <v-col cols="6">
        <participant-select
          v-model="reporter"
          label="Reporter"
          hint="The participant who reported the incident."
          clearable
          required
          :project="project"
          name="Reporter"
          :rules="[required_and_only_one]"
        />
      </v-col>
      <v-col cols="6">
        <participant-select
          v-model="commander"
          label="Incident Commander"
          hint="The participant acting as incident commander."
          clearable
          required
          :project="project"
          name="Incident Commander"
          :rules="[required_and_only_one]"
        />
      </v-col>
      <v-col cols="6">
        <project-select v-model="project" />
      </v-col>
      <v-col cols="6">
        <incident-type-select v-model="incident_type" :project="project" />
      </v-col>
      <v-col cols="6">
        <incident-severity-select v-model="incident_severity" :project="project" />
      </v-col>
      <v-col cols="6">
        <incident-priority-select v-model="incident_priority" :project="project" :status="status" />
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          hint="The status of the incident."
        />
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="visibility"
          label="Visibility"
          :items="visibilities"
          hint="The visibilty of the incident."
        />
      </v-col>
      <v-col cols="12">
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Reported At" v-model="reported_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Stable At" v-model="stable_at" />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12">
        <tag-filter-auto-complete
          label="Tags"
          v-model="tags"
          :project="project"
          model="incident"
          :model-id="id"
          show-copy
        />
      </v-col>
      <v-col cols="12">
        <incident-filter-combobox label="Duplicates" v-model="duplicates" :project="project" />
      </v-col>
      <v-col cols="12">
        <case-filter-combobox label="Cases" v-model="cases" />
      </v-col>
      <v-col cols="12" v-show="false">
        <v-text-field v-model="project" name="project" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"

import CaseFilterCombobox from "@/case/CaseFilterCombobox.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"
import IncidentFilterCombobox from "@/incident/IncidentFilterCombobox.vue"
import IncidentPrioritySelect from "@/incident/priority/IncidentPrioritySelect.vue"
import IncidentSeveritySelect from "@/incident/severity/IncidentSeveritySelect.vue"
import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import ParticipantSelect from "@/components/ParticipantSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "IncidentDetailsTab",

  components: {
    CaseFilterCombobox,
    DateTimePickerMenu,
    IncidentFilterCombobox,
    IncidentPrioritySelect,
    IncidentSeveritySelect,
    IncidentTypeSelect,
    ParticipantSelect,
    ProjectSelect,
    TagFilterAutoComplete,
  },

  data() {
    return {
      statuses: ["Active", "Stable", "Closed"],
      visibilities: ["Open", "Restricted"],
      required_and_only_one: (value) => {
        if (!value || value.length == 0) {
          return "This field is required"
        }
        if (value && value.length > 1) {
          return "Only one is allowed"
        }
        return true
      },
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.cases",
      "selected.commander",
      "selected.created_at",
      "selected.description",
      "selected.duplicates",
      "selected.id",
      "selected.incident_priority",
      "selected.incident_severity",
      "selected.incident_type",
      "selected.name",
      "selected.project",
      "selected.reported_at",
      "selected.reporter",
      "selected.resolution",
      "selected.stable_at",
      "selected.status",
      "selected.tags",
      "selected.terms",
      "selected.title",
      "selected.visibility",
    ]),
  },
}
</script>
