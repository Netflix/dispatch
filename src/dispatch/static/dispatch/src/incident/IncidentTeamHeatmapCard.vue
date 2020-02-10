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
    return {
      series: [
        {
          name: "Metric1",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric2",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric3",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric4",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric5",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric6",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric7",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric8",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        },
        {
          name: "Metric9",
          data: generateData(18, {
            min: 0,
            max: 90
          })
        }
      ],
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
    }
  }
}
</script>
