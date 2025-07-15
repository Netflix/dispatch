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
            <v-btn color="primary" @click="autoFillReport" :loading="loading">
              Auto-fill Report
            </v-btn>
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
    return {loading: false}
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
      "report.executive.next_steps",
    ]),
  },

  methods: {
    ...mapActions("incident", ["closeReportDialog", "createReport", "generateTacticalReport"]),

    async autoFillReport() {
      this.loading = true
      try {
        const response = await this.generateTacticalReport()
        console.log("this is the response")
        console.log(response)
        if (response && response.data && response.data.tactical_report) {
          const report = response.data.tactical_report

          // Create a new tactical report object with the generated content
          const tacticalReport = {
            conditions: report.conditions,
            actions: report.actions,
            needs: report.needs,
          }

          // Update the report data in the parent component
          this.$emit("update:report", {
            type: "tactical",
            tactical: tacticalReport,
          })

          this.$store.commit(
            "notification_backend/addBeNotification",
            { text: "Tactical report generated successfully.", type: "success" },
            { root: true }
          )
        } else if (response && response.data && response.data.error_message) {
          this.$store.commit(
            "notification_backend/addBeNotification",
            { text: response.data.error_message, type: "error" },
            { root: true }
          )
        }
      } catch (error) {
        this.$store.commit(
          "notification_backend/addBeNotification",
          { text: "Failed to generate tactical report.", type: "error" },
          { root: true }
        )
        console.error("Error generating tactical report:", error)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
