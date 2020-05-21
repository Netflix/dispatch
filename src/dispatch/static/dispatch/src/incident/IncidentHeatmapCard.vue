<template>
  <v-card>
    <v-card-title>Heatmap</v-card-title>
    <apexchart type="heatmap" height="350" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentHeatMapChartCard",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    },
    loading: {
      type: Boolean,
      default: function() {
        return false
      }
    }
  },
  components: {
    apexchart: VueApexCharts
  },

  computed: {
    chartOptions: {
      chart: {
        height: 350,
        type: "heatmap"
      },
      dataLabels: {
        enabled: false
      },
      colors: ["#008FFB"],
      title: {
        text: "HeatMap Chart (Single color)"
      }
    }
  },
  series() {
    let series = { name: "Weekday", data: [] }
  }
}
</script>
