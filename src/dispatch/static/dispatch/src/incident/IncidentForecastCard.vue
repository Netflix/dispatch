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
  props: {
    value: {
      type: String,
      default: function() {
        return "all"
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
          height: 350,
          type: "line",
          toolbar: {
            show: false
          }
        },
        dataLabels: {
          enabled: true
        },
        stroke: {
          curve: "smooth"
        },
        tooltip: {
          x: {
            format: "MMM yyyy"
          }
        },
        markers: {
          size: 1
        },
        xaxis: {
          categories: this.categories,
          type: "datetime",
          tickAmount: 6
        },
        yaxis: {
          min: 0,
          title: {
            text: "Incidents"
          }
        },
        legend: {
          position: "top"
        }
      }
    }
  },
  data() {
    return {
      loading: false,
      series: [],
      categories: []
    }
  },

  methods: {
    fetchData() {
      this.loading = "error"
      IncidentApi.getMetricForecast(this.value).then(response => {
        this.loading = false
        this.series = response.data.series
        this.categories = response.data.categories
      })
    }
  },

  mounted() {
    this.fetchData()
  }
}
</script>
