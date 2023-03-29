<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <ValidationProvider name="Title" rules="required" immediate>
          <v-text-field
            v-model="title"
            slot-scope="{ errors, valid }"
            :error-messages="errors"
            :success="valid"
            label="Title"
            hint="Title of the case."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs12>
        <ValidationProvider name="Description" rules="required" immediate>
          <v-textarea
            v-model="description"
            slot-scope="{ errors, valid }"
            :error-messages="errors"
            :success="valid"
            label="Description"
            hint="Description of the case."
            clearable
            required
          />
        </ValidationProvider>
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="resolution_reason"
          label="Resolution Reason"
          :items="resolutionReasons"
          hint="The general reason why a given case was resolved."
        />
      </v-flex>
      <v-flex xs12>
        <v-textarea
          v-model="resolution"
          label="Resolution"
          hint="Description of the actions taken to resolve the case."
          clearable
        />
      </v-flex>
      <v-flex xs12>
        <participant-select
          v-model="assignee"
          label="Assignee"
          hint="The organization member to which the case is assigned."
          clearable
          :project="project"
        />
      </v-flex>
      <v-flex xs6>
        <project-select v-model="project" />
      </v-flex>
      <v-flex xs6>
        <case-type-select v-model="case_type" :project="project" />
      </v-flex>
      <v-flex xs6>
        <case-severity-select v-model="case_severity" :project="project" />
      </v-flex>
      <v-flex xs6>
        <case-priority-select v-model="case_priority" :project="project" />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          hint="The status of the case."
        />
      </v-flex>
      <v-flex xs6>
        <v-select
          v-model="visibility"
          label="Visibility"
          :items="visibilities"
          hint="The visibilty of the case."
        />
      </v-flex>
      <v-flex xs12>
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Reported At" v-model="reported_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Triage At" v-model="triage_at" />
          </v-col>
        </v-row>
      </v-flex>
      <v-flex xs12>
        <v-row>
          <v-col cols="6">
            <date-time-picker-menu label="Escalated At" v-model="escalated_at" />
          </v-col>
          <v-col cols="6">
            <date-time-picker-menu label="Closed At" v-model="closed_at" />
          </v-col>
        </v-row>
      </v-flex>
      <v-flex xs12>
        <tag-filter-auto-complete label="Tags" v-model="tags" model="case" :model-id="id" />
      </v-flex>
      <v-flex xs12>
        <case-filter-combobox label="Related" v-model="related" :project="project" />
      </v-flex>
      <v-flex xs12>
        <case-filter-combobox label="Duplicates" v-model="duplicates" :project="project" />
      </v-flex>
      <v-flex xs12>
        <incident-filter-combobox label="Incidents" v-model="incidents" :project="project" />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { ValidationProvider, extend } from "vee-validate"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"

import CaseFilterCombobox from "@/case/CaseFilterCombobox.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import CaseSeveritySelect from "@/case/severity/CaseSeveritySelect.vue"
import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"
import IncidentFilterCombobox from "@/incident/IncidentFilterCombobox.vue"
import ParticipantSelect from "@/incident/ParticipantSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "CaseDetailsTab",

  components: {
    CaseFilterCombobox,
    CasePrioritySelect,
    CaseSeveritySelect,
    CaseTypeSelect,
    DateTimePickerMenu,
    IncidentFilterCombobox,
    ParticipantSelect,
    ProjectSelect,
    TagFilterAutoComplete,
    ValidationProvider,
  },

  data() {
    return {
      statuses: ["New", "Triage", "Escalated", "Closed"],
      visibilities: ["Open", "Restricted"],
      resolutionReasons: ["False Positive", "User Acknowledged", "Mitigated", "Escalated"],
    }
  },

  computed: {
    ...mapFields("case_management", [
      "selected.assignee",
      "selected.case_priority",
      "selected.case_severity",
      "selected.case_type",
      "selected.closed_at",
      "selected.description",
      "selected.duplicates",
      "selected.escalated_at",
      "selected.id",
      "selected.incidents",
      "selected.name",
      "selected.project",
      "selected.related",
      "selected.reported_at",
      "selected.resolution_reason",
      "selected.resolution",
      "selected.signals",
      "selected.status",
      "selected.tags",
      "selected.title",
      "selected.triage_at",
      "selected.visibility",
    ]),
  },
}
</script>
