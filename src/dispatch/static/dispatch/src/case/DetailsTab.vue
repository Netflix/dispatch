<template>
  <v-container grid-list-md>
    <v-row no-gutters>
      <v-col cols="3" class="pr-1">
        <case-type-select v-model="case_type" :project="project" />
      </v-col>
      <v-col cols="3" class="pr-1">
        <v-select
          v-model="status"
          label="Status"
          :items="statuses"
          hint="The status of the case."
        />
      </v-col>
      <v-col cols="3" class="pr-1">
        <case-severity-select v-model="case_severity" :project="project" />
      </v-col>
      <v-col cols="3" class="pr-1">
        <case-priority-select v-model="case_priority" :project="project" />
      </v-col>
      <v-col cols="3"> </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <v-textarea
          v-model="description"
          label="Description"
          hint="Description of the case."
          clearable
          filled
        />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <v-textarea
          v-model="resolution"
          label="Resolution"
          hint="Description of the actions taken to resolve the case."
          clearable
          filled
        />
      </v-col>
    </v-row>
    <chip-list label="Tags" v-model="tags" :project="project" />
    <chip-list label="Related Cases" v-model="related" :project="project" />
    <chip-list label="Duplicate Cases" v-model="duplicates" :project="project" />
    <chip-list label="Linked Incidents" v-model="incidents" :project="project" />      
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import CaseSeveritySelect from "@/case/severity/CaseSeveritySelect.vue"
import SignalFilterCombobox from "@/signal/SignalFilterCombobox.vue"
import CaseTypeSelect from "@/case/type/CaseTypeSelect.vue"
import ChipList from "@/components/ChipList.vue"

export default {
  name: "CaseDetailsTab",

  components: {
    CasePrioritySelect,
    CaseSeveritySelect,
    CaseTypeSelect,
    ChipList,

  },

  data() {
    return {
      statuses: ["New", "Triage", "Escalated", "Closed"],
      visibilities: ["Open", "Restricted"],
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
      "selected.signals",
      "selected.project",
      "selected.related",
      "selected.reported_at",
      "selected.resolution",
      "selected.status",
      "selected.tags",
      "selected.title",
      "selected.triage_at",
      "selected.visibility",
    ]),
  },
}
</script>
