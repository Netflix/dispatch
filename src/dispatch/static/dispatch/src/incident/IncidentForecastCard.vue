<template>
  <dashboard-card
    :loading="loading"
    type="line"
    :options="chartOptions"
    :series="series"
    title="Forecast"
  />
</template>

<script>
import IncidentApi from "@/incident/api"
import DashboardCard from "@/dashboard/DashboardCard.vue"

export default {
  name: "IncidentForecastCard",

  components: {
    DashboardCard,
  },

  props: {
    filterOptions: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  computed: {
    chartOptions() {
      return {
        chart: {
          height: 350,
          type: "line",
        },
        dataLabels: {
          enabled: true,
        },
        noData: {
          text: "Not enough data to create a forecast.",
          align: "center",
          verticalAlign: "middle",
          offsetX: 0,
          offsetY: 0,
          style: {
            color: undefined,
            fontSize: "14px",
            fontFamily: undefined,
          },
        },
        stroke: {
          curve: "smooth",
        },
        tooltip: {
          x: {
            format: "MMM yyyy",
          },
        },
        markers: {
          size: 1,
        },
        xaxis: {
          categories: this.categories,
          type: "datetime",
          tickAmount: 6,
        },
        yaxis: {
          min: 0,
          title: {
            text: "Incidents",
          },
        },
        legend: {
          position: "top",
        },
      }
    },
  },
  data() {
    return {
      loading: false,
      series: [],
      categories: [],
    }
  },

  methods: {
    fetchData() {
      this.loading = "error"
      let params = this.filterOptions || {}
      console.log(this.filterOptions)
      IncidentApi.getMetricForecast(params).then((response) => {
        this.loading = false
        this.series = response.data.series
        this.categories = response.data.categories
      })
    },
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.filterOptions],
      () => {
        this.fetchData()
      }
    )
  },
}
</script>
