<template>
  <v-card>
    <v-card-title>Priorities</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentPriorityBarChartCard",

  components: {
    apexchart: VueApexCharts
  },
  data() {
    return {
      series: [
        {
          name: "Low",
          data: [44, 55, 41, 67, 22, 43, 21, 49]
        },
        {
          name: "Medium",
          data: [13, 23, 20, 8, 13, 27, 33, 12]
        },
        {
          name: "High",
          data: [11, 17, 15, 15, 21, 14, 15, 13]
        }
      ],
      chartOptions: {
        chart: {
          type: "bar",
          height: 350,
          stacked: true,
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
