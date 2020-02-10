<template>
  <v-card>
    <v-card-title>Resolve Time</v-card-title>
    <apexchart type="line" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentResolveTimeCard",

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
