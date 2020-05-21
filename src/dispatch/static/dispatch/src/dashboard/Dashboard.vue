<template>
  <v-layout>
    <dialog-filter @update="update" />
    <v-tabs>
      <v-tab>Incidents</v-tab>
      <v-tab-item>
        <incident-overview></incident-overview>
      </v-tab-item>
    </v-tabs>
  </v-layout>
</template>

<script>
import IncidentOverview from "@/dashboard/IncidentOverview.vue"

export default {
  name: "DispatchDashboard",

  components: {
    IncidentOverview
  },

  data() {
    return {
      tab: null
    }
  }
}
</script>
