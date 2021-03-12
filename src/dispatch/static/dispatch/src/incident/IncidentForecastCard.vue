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
import SearchUtils from "@/search/utils"

export default {
  name: "IncidentForecastCard",
  props: {
    value: {
      type: Object,
      default: function() {
        return {}
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
      let expression = SearchUtils.createFilterExpression(this.value)
      let params = { filter: JSON.stringify(expression) }
      IncidentApi.getMetricForecast(params).then(response => {
        this.loading = false
        this.series = response.data.series
        this.categories = response.data.categories
      })
    }
  },

  watch: {
    value: function() {
      this.fetchData()
    }
  }
}
</script>
