<template>
  <v-card :loading="loading">
    <v-card-title>Priorities</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { countBy, isArray, mergeWith, forEach, map, find, sortBy } from "lodash"

import VueApexCharts from "vue-apexcharts"
import IncidentPriorityApi from "@/incident_priority/api"
export default {
  name: "IncidentPriorityBarChartCard",

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
      priorities: []
    }
  },

  created: function() {
    IncidentPriorityApi.getAll().then(response => {
      this.priorities = map(response.data.items, "name")
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
        colors: ["#FF4560", "#FEB019", "#008FFB"],
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
      let priorities = this.priorities
      forEach(this.value, function(value) {
        let priorityCounts = map(
          countBy(value, function(item) {
            return item.incident_priority.name
          }),
          function(value, key) {
            return { name: key, data: [value] }
          }
        )

        forEach(priorities, function(priority) {
          let found = find(priorityCounts, { name: priority })
          if (!found) {
            priorityCounts.push({ name: priority, data: [0] })
          }
        })
        series = mergeWith(series, priorityCounts, function(objValue, srcValue) {
          if (isArray(objValue)) {
            return objValue.concat(srcValue)
          }
        })
      })

      // sort
      series = sortBy(series, function(obj) {
        return priorities.indexOf(obj.name)
      })
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
