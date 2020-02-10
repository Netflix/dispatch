<template>
  <v-card>
    <v-card-title>Active Time</v-card-title>
    <apexchart type="line" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentActiveTimeCard",

  components: {
    apexchart: VueApexCharts
  },
  data() {
    return {
      series: [
        {
          name: "Predicted",
          data: [20, 25, 30, 32, 30, 29, 30]
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
        xaxis: {
          categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
          title: {
            text: "Month"
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
        yaxis: {
          title: {
            text: "Days"
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
