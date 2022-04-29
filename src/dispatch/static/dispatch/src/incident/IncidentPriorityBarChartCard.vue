<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Priorities"
  />
</template>

<script>
import { map, sortBy } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"
import IncidentPriorityApi from "@/incident_priority/api"

export default {
  name: "IncidentPriorityBarChartCard",

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

  data() {
    return {
      priorities: [],
    }
  },

  created: function () {
    IncidentPriorityApi.getAll().then((response) => {
      this.priorities = [
        ...new Set(
          map(
            sortBy(response.data.items, function (value) {
              return value.view_order
            }),
            "name"
          )
        ),
      ]
    })
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
        responsive: [
          {
            options: {
              legend: {
                position: "top",
              },
            },
          },
        ],
        colors: [
          function ({ seriesIndex, w }) {
            for (let i = 0; i < w.config.series[seriesIndex].data.length; i++) {
              if (w.config.series[seriesIndex].data[i].items.length > 0) {
                return w.config.series[seriesIndex].data[i].items[0].incident_priority.color
              }
            }
            return "#008FFB"
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
          position: "top",
        },
      }
    },
    series() {
      let series = DashboardUtils.createCountedSeriesData(
        this.value,
        "incident_priority.name",
        this.priorities
      )
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    },
  },
}
</script>
