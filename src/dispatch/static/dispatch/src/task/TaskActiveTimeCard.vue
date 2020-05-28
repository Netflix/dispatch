<template>
  <v-card :loading="loading">
    <v-card-title>Mean Resolve Time (Created -> Resolved)</v-card-title>
    <apexchart type="line" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { forEach, sumBy } from "lodash"
import differenceInHours from "date-fns/differenceInHours"
import parseISO from "date-fns/parseISO"
import VueApexCharts from "vue-apexcharts"
export default {
  name: "TaskActiveTimeCard",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    },
    interval: {
      type: String,
      default: function() {
        return "Month"
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
    return {}
  },

  computed: {
    series() {
      let series = { name: "Average Hours Active", data: [] }
      forEach(this.value, function(value) {
        series.data.push(
          Math.round(
            sumBy(value, function(item) {
              let endTime = new Date().toISOString()
              if (item.resolved_at) {
                endTime = item.resolved_at
              }
              return differenceInHours(parseISO(endTime), parseISO(item.created_at))
            }) / value.length
          )
        )
      })

      return [series]
    },
    chartOptions() {
      return {
        chart: {
          height: 350,
          type: "line",
          toolbar: {
            show: false
          }
        },
        xaxis: {
          categories: Object.keys(this.value) || [],
          title: {
            text: this.interval
          }
        },
        dataLabels: {
          enabled: true
        },
        stroke: {
          curve: "smooth"
        },
        markers: {
          size: 1
        },
        yaxis: {
          title: {
            text: "Hours"
          }
        },
        legend: {
          position: "top"
        }
      }
    }
  }
}
</script>
