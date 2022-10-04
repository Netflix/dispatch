<template>
  <v-dialog v-model="showEscalateDialog" persistent max-width="800px">
    <v-card v-if="incidentSelected.id">
      <v-card-title>
        <span class="headline">Case Escalated</span>
      </v-card-title>
      <v-card-text>
        <report-receipt-resources />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" text @click="closeEscalateDialog()"> Close </v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-else>
      <v-card-title>
        <span class="headline">Escalate Case?</span>
      </v-card-title>
      <v-card-text>
        Update the fields or accept the pre-filled defaults.
        <report-submission-form />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" text @click="closeEscalateDialog()"> Cancel </v-btn>
        <v-btn color="red en-1" text :loading="loading" @click="escalate(incidentSelected)">
          Escalate
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import ReportSubmissionForm from "@/incident/ReportSubmissionForm.vue"
import ReportReceiptResources from "@/incident/ReportReceiptResources.vue"

export default {
  name: "CaseEscalateDialog",

  data() {
    return {}
  },

  components: {
    ReportSubmissionForm,
    ReportReceiptResources,
  },

  computed: {
    ...mapFields("incident", {
      incidentPriority: "selected.incident_priority",
      incidentType: "selected.incident_type",
      incidentTitle: "selected.title",
      incidentTags: "selected.tags",
      incidentDescription: "selected.description",
      incidentLoading: "selected.loading",
      incidentProject: "selected.project",
      incidentId: "selected.id",
      incidentSelected: "selected",
    }),
    ...mapFields("case_management", {
      showEscalateDialog: "dialogs.showEscalateDialog",
      loading: "selected.loading",
      caseId: "selected.id",
      caseTitle: "selected.title",
      caseProject: "selected.project",
      caseDescription: "selected.description",
      caseType: "selected.case_type",
      casePriority: "selected.case_priority",
      caseSeverity: "selected.case_severity",
    }),
  },

  methods: {
    ...mapActions("case_management", ["getDetails", "closeEscalateDialog", "escalate"]),
    ...mapActions("incident", ["report", "resetSelected"]),
  },

  created() {
    this.$watch(
      (vm) => [vm.caseTitle, vm.caseProject, vm.caseDescription],
      () => {
        this.incidentTitle = this.caseTitle
        this.incidentProject = this.caseProject
        this.incidentDescription = this.caseDescription
      }
    )
  },
}
</script>
