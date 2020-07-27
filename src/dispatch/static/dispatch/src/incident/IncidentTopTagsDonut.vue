<template>
  <v-card :loading="loading">
    <v-card-title>Common Tags</v-card-title>
    <apexchart type="donut" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { forEach, countBy, chain, map } from "lodash"
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentTopTagsDonutCard",

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

  computed: {
    chartOptions() {
      return {
        chart: {
          type: "donut",
          height: 350,
          toolbar: {
            show: false
          }
        },
        tooltip: {
          enabled: false
        },
        dataLabels: {
          enabled: false
        },
        labels: this.labels,
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true
              },
              total: {
                show: true,
                label: "Total"
              }
            }
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
        legend: {
          position: "top"
        }
      }
    },
    summaryData() {
      let allTags = []
      forEach(this.value, function(value) {
        allTags.push(...value.tags)
      })
      let countByName = countBy(allTags, "name")
      var sorted = chain(countByName)
        .map(function(cnt, name) {
          return {
            name: name,
            count: cnt
          }
        })
        .sortBy("count")
        .value()
      return sorted.slice(Math.max(sorted.length - 10, 0))
    },
    series() {
      return map(this.summaryData, "count")
    },
    labels() {
      return map(this.summaryData, "name")
    }
  }
}
</script>
