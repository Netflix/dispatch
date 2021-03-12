<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Primary Location"
  />
</template>

<script>
import { forEach } from "lodash"
import DashboardUtils from "@/dashboard/utils"
import DashboardCard from "@/dashboard/DashboardCard.vue"

export default {
  name: "IncidentPrimaryLocationBarChartCard",

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
      let allLocations = []
      forEach(this.value, function(value) {
        forEach(value, function(value) {
          allLocations.push(value.primary_location)
        })
      })
      let series = DashboardUtils.createCountedSeriesData(this.value, "primary_location", [
        ...new Set(allLocations)
      ])
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
