<template>
  <v-card :loading="loading">
    <v-card-title>Priorities</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { countBy, forEach } from "lodash"

import VueApexCharts from "vue-apexcharts"
export default {
  name: "TaskIncidentPriorityBarChartCard",

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

  data() {
    return {
      order: ["High", "Medium", "Low", "Info"]
    }
  },

  computed: {
    chartOptions() {
      return {
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
        colors: ["#FF4560", "#FEB019", "#00E396", "#008FFB"],
        xaxis: {
          categories: this.categoryData || [],
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
    },
    series() {
      let aggCount = {}
      forEach(this.value, function(value) {
        let count = countBy(value, function(item) {
          return item.incident.incident_priority.name
        })

        forEach(count, function(value, key) {
          if (aggCount[key]) {
            aggCount[key].push(value)
          } else {
            aggCount[key] = [value]
          }
        })
      })

      let series = []
      forEach(this.order, function(o) {
        if (aggCount[o]) {
          series.push({ name: o, data: aggCount[o] })
        } else {
          series.push({ name: o, data: [0] })
        }
      })
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
