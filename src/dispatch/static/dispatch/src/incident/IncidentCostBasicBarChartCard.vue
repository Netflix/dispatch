<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Cost"
  />
</template>

<script>
import { map } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"

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
          enabled: false
        },
        tooltip: {
          enabled: false
        }
      }
    },
    series() {
      return [{ data: map(this.value, "cost") }]
    },
    categoryData() {
      return map(this.value, "name")
    }
  }
}
</script>
