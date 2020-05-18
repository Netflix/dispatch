<template>
  <v-card :loading="loading">
    <v-card-title>Hours Active</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { forEach, map } from "lodash"
import differenceInHours from "date-fns/differenceInHours"
import parseISO from "date-fns/parseISO"

import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentCostBasicBarChartCard",

  props: {
    value: {
      type: Array,
      default: function() {
        return []
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

  data() {
    return {}
  },

  computed: {
    chartOptions() {
      return {
        chart: {
          type: "bar",
          height: 350,
          toolbar: {
            show: false
          }
        },
        plotOptions: {
          bar: {
            horizontal: true
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
          categories: this.categoryData || [],
          title: {
            text: "Hours"
          }
        },
        fill: {
          opacity: 1
        },
        legend: {
          position: "top"
        },
        dataLabels: {
          enabled: false
        },
        tooltip: {
          enabled: false
        }
      }
    },
    series() {
      let series = { name: "Days Active", data: [] }
      forEach(this.value, function(value) {
        var endTime = new Date().toISOString()
        if (value.stable_at) {
          endTime = value.stable_at
        }
        var numHours = differenceInHours(parseISO(endTime), parseISO(value.reported_at))
        series.data.push(numHours)
      })
      return [series]
    },
    categoryData() {
      return map(this.value, "name")
    }
  }
}
</script>
