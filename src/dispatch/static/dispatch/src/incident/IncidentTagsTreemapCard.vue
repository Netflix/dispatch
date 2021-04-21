<template>
  <dashboard-card
    :loading="loading"
    type="treemap"
    :options="chartOptions"
    :series="series"
    title="Tag Treemap"
  />
</template>

<script>
import { forEach, countBy, sortBy, groupBy } from "lodash"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"

export default {
  name: "IncidentTreeMapCard",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
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

  computed: {
    chartOptions() {
      return {
        chart: {
          type: "treemap",
          height: 350,
          toolbar: {
            show: false,
          },
        },
        colors: DashboardUtils.defaultColorTheme(),
        responsive: [
          {
            options: {
              legend: {
                position: "top",
              },
            },
          },
        ],
        legend: {
          position: "top",
        },
      }
    },
    series() {
      // get all possible tags
      let allTags = []
      forEach(this.value, function (value) {
        allTags.push(...value.tags)
      })

      let tagSeries = []
      forEach(
        groupBy(allTags, function (value) {
          return value.tag_type.name
        }),
        function (value, key) {
          let tagCount = countBy(value, "name")
          let data = sortBy(
            Object.keys(tagCount).map((key) => ({ x: key, y: tagCount[key] })),
            ["y"]
          )
          tagSeries.push({ name: key, data: data })
        }
      )
      return tagSeries
    },
  },
}
</script>
