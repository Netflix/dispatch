<template>
  <v-card :loading="loading">
    <v-card-title>Forecast</v-card-title>
    <apexchart type="line" height="250" :options="chartOptions" :series="series"></apexchart>
    <template slot="progress">
      <v-progress-linear color="info" indeterminate></v-progress-linear>
    </template>
  </v-card>
</template>

<script>
import VueApexCharts from "vue-apexcharts"
import IncidentApi from "@/incident/api"
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
    apexchart: VueApexCharts
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
      this.loading = true
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
