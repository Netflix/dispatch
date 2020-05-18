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
  name: "IncidentPriorityBasicBarChartCard",

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
          toolbar: {
            show: false
          }
        },
        colors: ["#FF4560", "#FEB019", "#00E396", "#008FFB"],
        plotOptions: {
          bar: {
            horizontal: false,
            distributed: true
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
        yaxis: {
          labels: {
            formatter: function(val) {
              return val.toFixed(0)
            }
          }
        },
        xaxis: {
          categories: this.categoryData || [],
          title: {
            text: "Priority"
          }
        },
        fill: {
          opacity: 1
        },
        legend: {
          show: false
        },
        dataLabels: {
          enabled: false
        },
        tooltip: {
          enabled: false
        }
      }
    },
    priorityCount() {
      return countBy(this.value, function(item) {
        return item.incident_priority.name
      })
    },
    series() {
      // sort values by custom sort
      var sortedSeries = []
      var priorityCount = this.priorityCount

      forEach(this.order, function(o) {
        if (priorityCount[o]) {
          sortedSeries.push(priorityCount[o])
        } else {
          sortedSeries.push(0)
        }
      })

      return [{ data: sortedSeries }]
    },
    categoryData() {
      return this.order
    }
  }
}
</script>
