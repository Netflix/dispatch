<template>
  <v-dialog v-model="showReportDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Create Report</span>
      </v-card-title>
      <v-card-text>
        <v-tabs color="primary" v-model="type" align-tabs="end">
          <v-tab key="tactical" value="tactical"> Tactical </v-tab>
          <v-tab key="executive" value="executive"> Executive </v-tab>
        </v-tabs>
        <v-window v-model="type">
          <v-window-item key="tactical" value="tactical">
            <v-card>
              <v-card-text>
                Tactical reports are only sent to incident participants and are generally used for
                status reports.
                <v-textarea
                  v-model="conditions"
                  label="Conditions"
                  hint="The current state of the incident."
                  clearable
                  auto-grow
                />
                <v-textarea
                  v-model="actions"
                  label="Actions"
                  hint="Any actions that are currently inflight."
                  clearable
                  auto-grow
                />
                <v-textarea
                  v-model="needs"
                  label="Needs"
                  hint="Any outstanding asks that you are waiting on."
                  clearable
                  auto-grow
                />
              </v-card-text>
            </v-card>
            <v-row class="mt-4 px-3">
              <v-col cols="auto">
                <v-btn
                  color="primary"
                  @click="generateTacticalReport"
                  :loading="tactical_report_loading"
                >
                  Draft with GenAI
                </v-btn>
              </v-col>
              <v-col cols="auto" class="d-flex align-center">
                <span v-if="tactical_report_loading" class="ml-2"
                  >AI-generated reports may be unreliable. Be sure to review the output before
                  saving.</span
                >
              </v-col>
            </v-row>
          </v-window-item>
          <v-window-item key="executive" value="executive">
            <v-card>
              <v-card-text>
                Executive reports are sent to incident participants in addition to executive
                distribution lists. These reports are generally more narrative driven and less
                detailed.
                <v-textarea
                  v-model="current_status"
                  label="Current Status"
                  hint="The current status of the incident."
                  clearable
                  auto-grow
                />
                <v-textarea
                  v-model="overview"
                  label="Overview"
                  hint="A brief overview of an incident."
                  clearable
                  auto-grow
                />
                <v-textarea
                  v-model="next_steps"
                  label="Next Steps"
                  hint="Steps that will be taken to resolve the incident"
                  clearable
                  auto-grow
                />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="closeReportDialog()"> Cancel </v-btn>
        <v-btn color="info" variant="text" @click="createReport()"> Create </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
export default {
  name: "IncidentReportDialog",
  data() {
    return { loading: false }
  },
  computed: {
    ...mapFields("incident", [
      "dialogs.showReportDialog",
      "report.type",
      "report.tactical.conditions",
      "report.tactical.actions",
      "report.tactical.needs",
      "report.tactical_report_loading",
      "report.executive.current_status",
      "report.executive.overview",
      "report.executive.next_steps",
    ]),
  },

  methods: {
    ...mapActions("incident", ["closeReportDialog", "createReport", "generateTacticalReport"]),
  },
}
</script>
