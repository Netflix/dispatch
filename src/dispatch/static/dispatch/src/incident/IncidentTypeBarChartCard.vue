<template>
  <v-card :loading="loading">
    <v-card-title>Types</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import _ from "lodash"

import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentBarChartCard",

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
    return {}
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
      let series = []
      _.forEach(this.value, function(value) {
        let typeCount = _.map(
          _.countBy(value, function(item) {
            return item.incident_type.name
          }),
          function(value, key) {
            return { name: key, data: [value] }
          }
        )

        series = _.mergeWith(series, typeCount, function(objValue, srcValue) {
          if (_.isArray(objValue)) {
            return objValue.concat(srcValue)
          }
        })
      })

      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
