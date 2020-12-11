<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Primary Teams"
  />
</template>

<script>
import { countBy, isArray, mergeWith, forEach, map } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
export default {
  name: "IncidentPrimaryTeamBarChartCard",

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
                position: "left"
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
          position: "right"
        }
      }
    },
    series() {
      let series = []
      forEach(this.value, function(value) {
        let typeCount = map(
          countBy(value, function(item) {
            return item.primary_team
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

      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
