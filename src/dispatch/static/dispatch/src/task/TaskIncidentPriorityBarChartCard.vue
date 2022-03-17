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
import { countBy, forEach } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"

export default {
  name: "TaskIncidentPriorityBarChartCard",

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
      order: ["High", "Medium", "Low"],
    }
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
          toolbar: {
            show: false,
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
        colors: ["#FF4560", "#FEB019", "#008FFB"],
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
      let aggCount = {}
      forEach(this.value, function (value) {
        let count = countBy(value, function (item) {
          return item.incident.incident_priority.name
        })

        forEach(count, function (value, key) {
          if (aggCount[key]) {
            aggCount[key].push(value)
          } else {
            aggCount[key] = [value]
          }
        })
      })

      let series = []
      forEach(this.order, function (o) {
        if (aggCount[o]) {
          series.push({ name: o, data: aggCount[o] })
        } else {
          series.push({ name: o, data: [0] })
        }
      })
      return series
    },
    categoryData() {
      return Object.keys(this.value)
    },
  },
}
</script>
