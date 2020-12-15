<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Types"
  />
</template>

<script>
import { countBy, isArray, mergeWith, forEach, map, find, filter } from "lodash"

import IncidentTypeApi from "@/incident_type/api"
import DashboardCard from "@/dashboard/DashboardCard.vue"
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
      type: [String, Boolean],
      default: function() {
        return false
      }
    }
  },

  components: {
    DashboardCard
  },

  data() {
    return {
      types: []
    }
  },

  created: function() {
    IncidentTypeApi.getAll({ itemsPerPage: -1 }).then(response => {
      this.types = map(
        filter(response.data.items, function(item) {
          return !item.exclude_from_metrics
        }),
        "name"
      )
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
      let types = this.types
      forEach(this.value, function(value) {
        let typeCounts = map(
          countBy(value, function(item) {
            return item.incident_type.name
          }),
          function(value, key) {
            return { name: key, data: [value] }
          }
        )

        forEach(types, function(type) {
          let found = find(typeCounts, { name: type })
          if (!found) {
            typeCounts.push({ name: type, data: [0] })
          }
        })
        series = mergeWith(series, typeCounts, function(objValue, srcValue) {
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
