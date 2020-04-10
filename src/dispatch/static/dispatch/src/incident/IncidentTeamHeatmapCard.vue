<template>
  <v-card>
    <v-card-title>Team</v-card-title>
    <apexchart type="heatmap" height="350" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentBarChartCard",

  components: {
    apexchart: VueApexCharts
  },
  data() {
    return {}
  }
}
</script>
