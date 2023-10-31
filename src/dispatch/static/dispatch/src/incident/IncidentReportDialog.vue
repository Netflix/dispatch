<template>
  <v-dialog v-model="show" persistent max-width="800px">
    <v-card>
      <v-card-title class="text-h6"> Latest Incident Reports </v-card-title>
    </v-card>
    <v-card-text>
      <v-card>
        <v-card-title class="text-h6"> Description </v-card-title>
        <v-card-text>{{ item.description }}</v-card-text>
      </v-card>
      <v-card>
        <v-card-text>
          <div class="text-h6 text--primary">Last Tactical Report</div>
          <div v-if="item.last_tactical_report">
            <p>As of {{ formatRelativeDate(item.last_tactical_report.created_at) }}</p>
            <p class="text-subtitle-1 text--primary">Conditions</p>
            <div>{{ item.last_tactical_report.details.conditions }}</div>
            <p class="text-subtitle-1 text--primary">Actions</p>
            <div>{{ item.last_tactical_report.details.actions }}</div>
            <p class="text-subtitle-1 text--primary">Needs</p>
            <div>{{ item.last_tactical_report.details.needs }}</div>
          </div>
          <div v-else>No tactical report available.</div>
        </v-card-text>
      </v-card>
      <v-card>
        <v-card-text>
          <div class="text-h6 text--primary">Last Executive Report</div>
          <div v-if="item.last_executive_report">
            <p>As of {{ formatRelativeDate(item.last_executive_report.created_at) }}</p>
            <p class="text-subtitle-1 text--primary">Current Status</p>
            <div>{{ item.last_executive_report.details.current_status }}</div>
            <p class="text-subtitle-1 text--primary">Overview</p>
            <div>{{ item.last_executive_report.details.overview }}</div>
            <p class="text-subtitle-1 text--primary">Next Steps</p>
            <div>{{ item.last_executive_report.details.next_steps }}</div>
          </div>
          <div v-else>No executive report available.</div>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-dialog>
</template>
<script>
import { formatRelativeDate } from "@/filters"

export default {
  name: "IncidentReportDialog",

  data() {
    return {
      show: false,
    }
  },

  setup() {
    return { formatRelativeDate }
  },
}
</script>
