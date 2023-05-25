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
import { map } from "lodash"

import CaseApi from "@/case/api"
import DashboardCard from "@/dashboard/DashboardCard.vue"
import DashboardUtils from "@/dashboard/utils"

export default {
  name: "CaseBarChartCard",

  components: {
    DashboardCard,
  },

  props: {
    value: {
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
      counts: [],
    }
  },

  created: function () {
    CaseApi.getTypeCount().then((response) => {
      console.log(response)
      this.types = map(response.data, (item) => item[0])
      this.counts = map(response.data, (item) => item[1])
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
          categories: this.types || [],
          title: {
            text: "Types",
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
      return [
        {
          name: "Types",
          data: this.counts,
        },
      ]
    },
  },
}
</script>
