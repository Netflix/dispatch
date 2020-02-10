<template>
  <v-layout wrap>
    <v-container fluid>
      <v-row dense>
        <v-col md="6">
          <incident-type-bar-chart-card></incident-type-bar-chart-card>
        </v-col>
        <v-col md="6">
          <incident-priority-bar-chart-card></incident-priority-bar-chart-card>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col md="6">
          <incident-active-time-card></incident-active-time-card>
        </v-col>
        <v-col md="6">
          <incident-resolve-time-card></incident-resolve-time-card>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col md="6">
          <incident-forecast-card></incident-forecast-card>
        </v-col>
        <v-col md="6">
          <incident-cost-bar-chart-card></incident-cost-bar-chart-card>
        </v-col>
      </v-row>
    </v-container>
  </v-layout>
</template>

<script>
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentForecastCard from "@/incident/IncidentForecastCard.vue"
import IncidentTeamHeatmapCard from "@/incident/IncidentTeamHeatmapCard.vue"
import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
export default {
  name: "IncidentDashboard",

  components: {
    IncidentTypeBarChartCard,
    IncidentForecastCard,
    IncidentTeamHeatmapCard,
    IncidentResolveTimeCard,
    IncidentActiveTimeCard,
    IncidentCostBarChartCard,
    IncidentPriorityBarChartCard
  },

  data() {
    return {}
  }
}
</script>
