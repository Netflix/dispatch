<template>
  <v-card>
    <v-card-title>Cost</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentCostBarChartCard",

  components: {
    apexchart: VueApexCharts
  },
  data() {
    return {
      series: [
        {
          name: "Studio",
          data: [44, 55, 41, 67, 22, 43, 21, 49]
        }
      ],
      chartOptions: {
        chart: {
          type: "bar",
          height: 350,
          toolbar: {
            show: false
          }
        },
        responsive: [
          {
            options: {
              legend: {
                position: "top"
              }
            }
          }
        ],
        xaxis: {
          categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
          title: {
            text: "Month"
          }
        },
        fill: {
          opacity: 1
        },
        legend: {
          position: "top"
        }
      }
    }
  }
}
</script>
