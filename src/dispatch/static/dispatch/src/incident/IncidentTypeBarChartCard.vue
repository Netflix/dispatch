<template>
  <v-card :loading="loading">
    <v-card-title>Types</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { countBy, isArray, mergeWith, forEach, map } from "lodash"

import VueApexCharts from "vue-apexcharts"
import IncidentTypeApi from "@/incident_type/api"
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
    return {
      types: []
    }
  },

  created: function() {
    IncidentTypeApi.getAll({ itemsPerPage: -1 }).then(response => {
      this.types = map(response.data.items, "name")
    })
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
      forEach(this.value, function(value) {
        let typeCount = map(
          countBy(value, function(item) {
            return item.incident_type.name
          }),
          function(value, key) {
            return { name: key, data: [value] }
          }
        )

        series = mergeWith(series, typeCount, function(objValue, srcValue) {
          if (isArray(objValue)) {
            return objValue.concat(srcValue)
          }
        })
      })

      // sort
      //series = sortBy(series, function(obj) {
      //  return types.indexOf(obj.name)
      //})
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
