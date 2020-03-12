<template>
  <v-layout>
    <v-tabs>
      <v-tab>Overview</v-tab>
      <v-tab>By Month</v-tab>
      <v-tab-item>
        <dashboard-overview></dashboard-overview>
      </v-tab-item>
      <v-tab-item>
        <dashboard-monthly></dashboard-monthly>
      </v-tab-item>
    </v-tabs>
  </v-layout>
</template>

<script>
import DashboardOverview from "@/dashboard/Overview.vue"
import DashboardMonthly from "@/dashboard/Monthly.vue"
import DashboardIncidentType from "@/dashboard/IncidentType.vue"

export default {
  name: "IncidentDashboard",

  components: {
    DashboardOverview,
    DashboardMonthly,
    DashboardIncidentType
  },

  data() {
    return {
      tab: null
    }
  }
}
</script>
