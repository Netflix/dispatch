<template>
  <dashboard-card
    :loading="loading"
    type="treemap"
    :options="chartOptions"
    :series="series"
    title="Common Tags"
  />
</template>

<script>
import { forEach, countBy, sortBy } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
export default {
  name: "IncidentTreeMapCard",

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
          type: "treemap",
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
        legend: {
          position: "top"
        }
      }
    },
    summaryData() {
      let allTags = []
      forEach(this.value, function(value) {
        allTags.push(...value.tags)
      })
      let tagCount = countBy(allTags, "name")
      return sortBy(
        Object.keys(tagCount).map(key => ({ x: key, y: tagCount[key] })),
        ["y"]
      )
    },
    series() {
      return [{ data: this.summaryData }]
    }
  }
}
</script>
