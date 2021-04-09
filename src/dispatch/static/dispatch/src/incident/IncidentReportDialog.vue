<template>
  <v-dialog v-model="show" persistent max-width="800px">
    <v-card elevation="0" outlined>
      <v-card-title class="title"> Latest Incident Reports </v-card-title>
    </v-card>
    <v-card-text>
      <v-card outlined>
        <v-card-title class="title"> Description </v-card-title>
        <v-card-text>{{ item.description }}</v-card-text>
      </v-card>
      <v-card outlined>
        <v-card-text>
          <div class="title text--primary">Last Tactical Report</div>
          <div v-if="item.last_tactical_report">
            <p>As of {{ item.last_tactical_report.created_at | formatDate }}</p>
            <p class="subtitle-1 text--primary">Conditions</p>
            <div>{{ item.last_tactical_report.details.conditions }}</div>
            <p class="subtitle-1 text--primary">Actions</p>
            <div>{{ item.last_tactical_report.details.actions }}</div>
            <p class="subtitle-1 text--primary">Needs</p>
            <div>{{ item.last_tactical_report.details.needs }}</div>
          </div>
          <div v-else>No tactical report available.</div>
        </v-card-text>
      </v-card>
      <v-card outlined>
        <v-card-text>
          <div class="title text--primary">Last Executive Report</div>
          <div v-if="item.last_executive_report">
            <p>As of {{ item.last_executive_report.created_at | formatDate }}</p>
            <p class="subtitle-1 text--primary">Current Status</p>
            <div>{{ item.last_executive_report.details.current_status }}</div>
            <p class="subtitle-1 text--primary">Overview</p>
            <div>{{ item.last_executive_report.details.overview }}</div>
            <p class="subtitle-1 text--primary">Next Steps</p>
            <div>{{ item.last_executive_report.details.next_steps }}</div>
          </div>
          <div v-else>No executive report available.</div>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-dialog>
</template>
<script>
export default {
  name: "IncidentReportDialog",

  data() {
    return {
      show: false,
    }
  },
}
</script>
