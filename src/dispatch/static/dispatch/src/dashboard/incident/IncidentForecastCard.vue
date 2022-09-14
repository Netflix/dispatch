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
import { mapFields } from "vuex-map-fields"
import SearchUtils from "@/search/utils"
import RouterUtils from "@/router/utils"
import IncidentApi from "@/incident/api"
import DashboardCard from "@/dashboard/DashboardCard.vue"

export default {
  name: "IncidentForecastCard",

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
  },

  computed: {
    ...mapFields("route", ["query"]),
    filterParam() {
      let params = {}
      let filters = RouterUtils.deserializeFilters(this.query) // Order matters as values will overwrite
      if (filters) {
        delete filters.reported_at
        delete filters.closed_at
        let expression = SearchUtils.createFilterExpression(filters, "Incident")
        if (expression.length != 0) {
          params = { filter: JSON.stringify({ and: expression }) }
        }
      }
      return params
    },
    chartOptions() {
      return {
        chart: {
          height: 350,
          type: "line",
          animations: {
            enabled: false,
          },
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
      this.loading = "primary"
      IncidentApi.getMetricForecast(this.filterParam).then((response) => {
        this.loading = false
        this.series = response.data.series
        this.categories = response.data.categories
      })
    },
  },

  created: function () {
    this.fetchData()
  },

  watch: {
    query: function () {
      this.fetchData()
    },
  },
}
</script>
