<template>
  <v-dialog v-model="showReportDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Create Report</span>
      </v-card-title>
      <v-card-text>
        <v-tabs color="primary" v-model="type" right>
          <v-tab key="tactical" href="#tactical">Tactical</v-tab>
          <v-tab key="executive" href="#executive">Executive</v-tab>
        </v-tabs>
        <v-tabs-items v-model="type">
          <v-tab-item key="tactical" value="tactical">
            <v-card elevation="0">
              <v-card-text>
                Tactical reports are only send to incident participants and are generally used for
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
          </v-tab-item>
          <v-tab-item key="executive" value="executive">
            <v-card elevation="0">
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
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="closeReportDialog()">
          Cancel
        </v-btn>
        <v-btn color="info" text @click="createReport()">
          Create
        </v-btn>
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
    return {}
  },
  computed: {
    ...mapFields("incident", [
      "dialogs.showReportDialog",
      "report.type",
      "report.tactical.conditions",
      "report.tactical.actions",
      "report.tactical.needs",
      "report.executive.current_status",
      "report.executive.overview",
      "report.executive.next_steps"
    ])
  },

  methods: {
    ...mapActions("incident", ["closeReportDialog", "createReport"])
  }
}
</script>
