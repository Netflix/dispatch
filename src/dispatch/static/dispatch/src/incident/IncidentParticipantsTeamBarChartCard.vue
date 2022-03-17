<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Participants Team"
  />
</template>

<script>
import { forEach } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"

export default {
  name: "IncidentParticipantsTeamBarChartCard",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    loading: {
      type: [String, Boolean],
      default: function () {
        return false
      },
    },
  },

  components: {
    DashboardCard,
  },

  computed: {
    chartOptions() {
      return {
        chart: {
          type: "bar",
          height: 350,
          stacked: true,
          animations: {
            enabled: false,
          },
          events: {
            dataPointSelection: (event, chartContext, config) => {
              var data = config.w.config.series[config.seriesIndex].data[config.dataPointIndex]
              this.$emit("detailsSelected", data.items)
            },
          },
        },
        colors: DashboardUtils.defaultColorTheme(),
        responsive: [
          {
            options: {
              legend: {
                position: "left",
              },
            },
          },
        ],
        xaxis: {
          categories: this.categoryData || [],
          title: {
            text: "Month",
          },
        },
        fill: {
          opacity: 1,
        },
        legend: {
          position: "right",
        },
      }
    },
    series() {
      let allTeams = []
      forEach(this.value, function (value) {
        forEach(value, function (value) {
          allTeams.push(value.participants_team)
        })
      })
      let series = DashboardUtils.createCountedSeriesData(this.value, "participants_team", [
        ...new Set(allTeams),
      ])
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    },
  },
}
</script>
