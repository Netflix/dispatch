<template>
  <v-layout wrap>
    <v-container fluid>
      <v-row dense>
        <v-col md="6">
          <v-select
            v-model="window"
            :items="windows"
            menu-props="auto"
            hide-details
            label="Select Window"
            single-line
            disabled
          ></v-select>
        </v-col>
        <v-col md="6">
          <v-select
            v-model="range"
            :items="ranges"
            menu-props="auto"
            hide-details
            label="Select Range"
            single-line
            disabled
          ></v-select>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col md="6">
          <incident-type-bar-chart-card
            v-model="groupedItems"
            :loading="loading"
          ></incident-type-bar-chart-card>
        </v-col>
        <v-col md="6">
          <incident-priority-bar-chart-card
            v-model="groupedItems"
            :loading="loading"
          ></incident-priority-bar-chart-card>
        </v-col>
      </v-row>
      <v-row dense>
        <v-col md="6">
          <incident-cost-bar-chart-card
            v-model="groupedItems"
            :loading="loading"
          ></incident-cost-bar-chart-card>
        </v-col>
        <v-col md="6"> </v-col>
      </v-row>
      <v-row dense>
        <v-col md="6">
          <incident-active-time-card
            v-model="groupedItems"
            :loading="loading"
          ></incident-active-time-card>
        </v-col>
        <v-col md="6">
          <incident-resolve-time-card
            v-model="groupedItems"
            :loading="loading"
          ></incident-resolve-time-card>
        </v-col>
      </v-row>
    </v-container>
  </v-layout>
</template>

<script>
import _ from "lodash"
import parseISO from "date-fns/parseISO"
import IncidentApi from "@/incident/api"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentForecastCard from "@/incident/IncidentForecastCard.vue"
import IncidentTeamHeatmapCard from "@/incident/IncidentTeamHeatmapCard.vue"
import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
export default {
  name: "IncidentDashboard",

  components: {
    IncidentTypeBarChartCard,
    IncidentForecastCard,
    IncidentTeamHeatmapCard,
    IncidentResolveTimeCard,
    IncidentActiveTimeCard,
    IncidentCostBarChartCard,
    IncidentPriorityBarChartCard
  },

  data() {
    return {
      loading: false,
      items: [],
      range: { text: "90 Days" },
      window: { text: "Month" },
      windows: [{ text: "Month" }, { text: "Year" }, { text: "Quarter" }],
      ranges: [{ text: "30 Days" }, { text: "90 Days" }, { text: "1 Year" }, { text: "2 Year" }]
    }
  },

  computed: {
    incidentsByYear() {
      return _.groupBy(this.items, function(item) {
        return parseISO(item.created_at).getYear()
      })
    },
    incidentsByMonth() {
      return _.groupBy(this.items, function(item) {
        return parseISO(item.created_at).toLocaleString("default", { month: "short" })
      })
    },
    incidentsByQuarter() {
      return _.groupBy(this.items, function(item) {
        return "Q" + Math.floor(parseISO(item.created_at).getMonth() + 3) / 3
      })
    },
    groupedItems() {
      return this.incidentsByMonth
    }
  },

  created() {
    this.loading = true
    // TODO make this reported_at
    IncidentApi.getAll({ itemsPerPage: 50, sortBy: ["created_at"], descending: [true] }).then(
      response => {
        this.items = _.sortBy(response.data.items, "created_at")
        this.loading = false
      }
    )
  }
}
</script>
