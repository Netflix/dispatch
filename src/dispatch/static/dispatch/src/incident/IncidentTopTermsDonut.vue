<template>
  <dashboard-card
    :loading="loading"
    type="donut"
    :options="chartOptions"
    :series="series"
    title="Common Terms"
  />
</template>

<script>
import { forEach, countBy, chain, map } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
export default {
  name: "IncidentTopTermsDonutCard",

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

  computed: {
    chartOptions() {
      return {
        chart: {
          type: "donut",
          height: 350,
          toolbar: {
            show: false
          }
        },
        tooltip: {
          enabled: false
        },
        dataLabels: {
          enabled: false
        },
        labels: this.labels,
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true
              },
              total: {
                show: true,
                label: "Total"
              }
            }
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
        legend: {
          position: "top"
        }
      }
    },
    summaryData() {
      let allTerms = []
      forEach(this.value, function(value) {
        allTerms.push(...value.terms)
      })
      let countByName = countBy(allTerms, "name")
      var sorted = chain(countByName)
        .map(function(cnt, name) {
          return {
            name: name,
            count: cnt
          }
        })
        .sortBy("count")
        .value()
      return sorted.slice(Math.max(sorted.length - 10, 0))
    },
    series() {
      return map(this.summaryData, "count")
    },
    labels() {
      return map(this.summaryData, "name")
    }
  }
}
</script>
