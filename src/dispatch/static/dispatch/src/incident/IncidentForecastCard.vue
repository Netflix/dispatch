<template>
  <v-card>
    <v-card-title>Forecast</v-card-title>
    <apexchart type="line" height="250" :options="chartOptions" :series="series"></apexchart>
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
          name: "High",
          data: [28, 29, 33, 36, 32, 32, 33]
        },
        {
          name: "Predicted",
          data: [20, 25, 30, 32, 30, 29, 30]
        },
        {
          name: "Low",
          data: [12, 11, 14, 18, 17, 13, 13]
        }
      ],
      chartOptions: {
        chart: {
          height: 350,
          type: "line",
          toolbar: {
            show: false
          }
        },
        dataLabels: {
          enabled: true
        },
        stroke: {
          curve: "smooth"
        },
        markers: {
          size: 1
        },
        xaxis: {
          categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
          title: {
            text: "Month"
          }
        },
        yaxis: {
          title: {
            text: "Count"
          },
          min: 5,
          max: 40
        },
        legend: {
          position: "top"
        }
      }
    }
  }
}
</script>
