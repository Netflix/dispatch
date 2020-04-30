<template>
  <v-card :loading="loading">
    <v-card-title>Cost</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { forEach, sumBy } from "lodash"
import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentCostBarChartCard",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
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
        yaxis: {
          labels: {
            show: false,
            formatter: function(val) {
              var formatter = new Intl.NumberFormat("en-US", {
                style: "currency",
                currency: "USD",
                maximumSignificantDigits: 6
              })

              return formatter.format(val) /* $2,500.00 */
            }
          }
        },
        fill: {
          opacity: 1
        },
        legend: {
          position: "top"
        },
        dataLabels: {
          enabled: true,
          formatter: function(val) {
            var formatter = new Intl.NumberFormat("en-US", {
              style: "currency",
              currency: "USD",
              maximumSignificantDigits: 6
            })

            return formatter.format(val) /* $2,500.00 */
          }
        }
      }
    },
    series() {
      let series = { name: "cost", data: [] }
      forEach(this.value, function(value) {
        series.data.push(sumBy(value, "cost"))
      })

      return [series]
    },
    categoryData() {
      return Object.keys(this.value)
    }
  }
}
</script>
