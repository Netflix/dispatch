<template>
  <v-card :loading="loading">
    <v-card-title>Cost</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import _ from "lodash"

import VueApexCharts from "vue-apexcharts"
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
            text: "Cost"
          },
          labels: {
            formatter: function(val) {
              var formatter = new Intl.NumberFormat("en-US", {
                style: "currency",
                currency: "USD"
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
          enabled: false
        },
        tooltip: {
          enabled: false
        }
      }
    },
    series() {
      return [{ data: _.map(this.value, "cost") }]
    },
    categoryData() {
      return _.map(this.value, "name")
    }
  }
}
</script>
