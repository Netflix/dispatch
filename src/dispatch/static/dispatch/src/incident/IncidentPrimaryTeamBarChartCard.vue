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
import { forEach } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"

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
        colors: DashboardUtils.defaultColorTheme(),
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
      let allTeams = []
      forEach(this.value, function(value) {
        forEach(value, function(value) {
          allTeams.push(value.primary_team)
        })
      })
      let series = DashboardUtils.createCountedSeriesData(this.value, "primary_team", [
        ...new Set(allTeams)
      ])
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
