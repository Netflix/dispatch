<template>
  <v-card :loading="loading">
    <v-card-title>Types</v-card-title>
    <apexchart type="bar" height="250" :options="chartOptions" :series="series"></apexchart>
  </v-card>
</template>

<script>
import { countBy } from "lodash"

import VueApexCharts from "vue-apexcharts"
export default {
  name: "IncidentTypeBasicBarChartCard",

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
            horizontal: false,
            distributed: true
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
            text: "Types"
          }
        },
        yaxis: {
          labels: {
            formatter: function(val) {
              return val.toFixed(0)
            }
          }
        },
        legend: {
          show: false
        },
        fill: {
          opacity: 1
        },
        dataLabels: {
          enabled: false
        },
        tooltip: {
          enabled: false
        }
      }
    },
    typeCount() {
      return countBy(this.value, function(item) {
        return item.incident_type.name
      })
    },
    series() {
      return [{ data: Object.values(this.typeCount) }]
    },
    categoryData() {
      return Object.keys(this.typeCount)
    }
  }
}
</script>
