<template>
<span>
  <incidents-drill-down-sheet :show="show" :items="items" />
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Priorities"
  />
</span>
</template>

<script>
import { map, sortBy } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"
import IncidentPriorityApi from "@/incident_priority/api"
import IncidentsDrillDownSheet from '@/dashboard/IncidentsDrillDownSheet.vue'
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
    IncidentsDrillDownSheet,
  },

  data() {
    return {
      priorities: [],
      items: [],
      show: false,
    }
  },

  created: function () {
    IncidentPriorityApi.getAll().then((response) => {
      this.priorities = map(
        sortBy(response.data.items, function (value) {
          return value.view_order
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
            show: false,
          },
          events: {
            dataPointSelection:  (event, chartContext, config) => {
              var data = config.w.config.series[config.seriesIndex].data[config.dataPointIndex];
              this.items = data.items
              this.show = true
            }
          }
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
        colors: ["#008FFB", "#FF4560", "#FEB019"],
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
