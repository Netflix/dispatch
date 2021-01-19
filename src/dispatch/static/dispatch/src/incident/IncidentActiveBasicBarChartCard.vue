<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Hours Active"
  />
</template>

<script>
import { forEach, map } from "lodash"
import differenceInHours from "date-fns/differenceInHours"
import parseISO from "date-fns/parseISO"

export default {
  name: "IncidentCostBasicBarChartCard",

  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    },
    loading: {
      type: [String, Boolean],
      default: function() {
        return false
      }
    }
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
          toolbar: {
            show: false
          }
        },
        plotOptions: {
          bar: {
            horizontal: true
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
            text: "Hours"
          }
        },
        fill: {
          opacity: 1
        },
        legend: {
          position: "top"
        },
        dataLabels: {
          enabled: false
        },
        tooltip: {
          enabled: false
        }
      }
    },
    series() {
      let series = { name: "Days Active", data: [] }
      forEach(this.value, function(value) {
        var endTime = new Date().toISOString()
        if (value.stable_at) {
          endTime = value.stable_at
        }
        var numHours = differenceInHours(parseISO(endTime), parseISO(value.reported_at))
        series.data.push(numHours)
      })
      return [series]
    },
    categoryData() {
      return map(this.value, "name")
    }
  }
}
</script>
