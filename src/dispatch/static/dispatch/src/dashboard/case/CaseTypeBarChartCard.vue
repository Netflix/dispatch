<template>
  <dashboard-card
    :loading="loading"
    type="bar"
    :options="chartOptions"
    :series="series"
    title="Types"
  />
</template>

<script>
import { map, filter } from "lodash"

import CaseTypeApi from "@/case/type/api"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"

export default {
  name: "CaseBarChartCard",

  components: {
    DashboardCard,
  },

  props: {
    modelValue: {
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

  data() {
    return {
      types: [],
    }
  },

  created: function () {
    CaseTypeApi.getAll({ itemsPerPage: -1 }).then((response) => {
      this.types = map(
        filter(response.data.items, function (item) {
          return !item.exclude_from_metrics
        }),
        "name"
      )
    })
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
          events: {
            dataPointSelection: (event, chartContext, config) => {
              var data = config.w.config.series[config.seriesIndex].data[config.dataPointIndex]
              this.$emit("detailsSelected", data.items)
            },
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
      return DashboardUtils.createCountedSeriesData(this.modelValue, "case_type.name", this.types)
    },
    categoryData() {
      return Object.keys(this.modelValue)
    },
  },
}
</script>
