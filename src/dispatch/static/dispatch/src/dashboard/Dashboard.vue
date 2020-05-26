<template>
  <v-layout>
    <v-tabs>
      <v-tab>Incidents</v-tab>
      <v-tab-item>
        <incident-overview></incident-overview>
      </v-tab-item>
      <v-tab>Tasks</v-tab>
      <v-tab-item>
        <task-overview></task-overview>
      </v-tab-item>
    </v-tabs>
  </v-layout>
</template>

<script>
import IncidentOverview from "@/dashboard/IncidentOverview.vue"
import TaskOverview from "@/dashboard/TaskOverview.vue"

export default {
  name: "DispatchDashboard",

  components: {
    IncidentOverview,
    TaskOverview
  },

  data() {
    return {
      tab: null
    }
  }
}
</script>
