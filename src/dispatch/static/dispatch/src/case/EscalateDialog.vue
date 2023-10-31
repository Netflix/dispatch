<template>
  <v-dialog v-model="showEscalateDialog" persistent max-width="800px">
    <v-card v-if="incidentSelected.id">
      <v-card-title>
        <span class="text-h5">Case Escalated</span>
      </v-card-title>
      <v-card-text>
        <report-receipt-resources />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeEscalateDialog()"> Close </v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-else>
      <v-card-title>
        <span class="text-h5">Escalate Case?</span>
      </v-card-title>
      <v-card-text>
        Update the fields or accept the pre-filled defaults.
        <report-submission-form incident-type="this.incidentType" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeEscalateDialog()"> Cancel </v-btn>
        <v-btn
          color="red en-1"
          variant="text"
          :loading="loading"
          @click="escalate(incidentSelected)"
        >
          Escalate
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ReportReceiptResources from "@/incident/ReportReceiptResources.vue"
import ReportSubmissionForm from "@/incident/ReportSubmissionForm.vue"

export default {
  name: "CaseEscalateDialog",

  data() {
    return {}
  },

  components: {
    ReportReceiptResources,
    ReportSubmissionForm,
  },

  computed: {
    ...mapFields("incident", {
      incidentDescription: "selected.description",
      incidentId: "selected.id",
      incidentLoading: "selected.loading",
      incidentPriority: "selected.incident_priority",
      incidentProject: "selected.project",
      incidentSelected: "selected",
      incidentTags: "selected.tags",
      incidentTitle: "selected.title",
      incidentType: "selected.incident_type",
    }),
    ...mapFields("case_management", {
      caseDescription: "selected.description",
      caseId: "selected.id",
      casePriority: "selected.case_priority",
      caseProject: "selected.project",
      caseSeverity: "selected.case_severity",
      caseTitle: "selected.title",
      caseType: "selected.case_type",
      loading: "selected.loading",
      showEscalateDialog: "dialogs.showEscalateDialog",
    }),
  },

  methods: {
    ...mapActions("case_management", ["getDetails", "closeEscalateDialog", "escalate"]),
    ...mapActions("incident", ["report", "resetSelected"]),
  },

  created() {
    this.$watch(
      (vm) => [vm.showEscalateDialog],
      () => {
        this.incidentDescription = this.caseDescription
        this.incidentTitle = this.caseTitle
        this.incidentProject = this.caseProject ? this.caseProject : null
        this.incidentType = this.caseType.incident_type ? this.caseType.incident_type : null
      }
    )
  },
}
</script>
