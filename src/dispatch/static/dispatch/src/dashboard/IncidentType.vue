<template>
  <v-layout wrap>
    <v-row dense>
      <v-col md="4">
        <v-card class="mx-auto">
          <v-card-title>Incidents</v-card-title>
          <v-card-text>
            <v-row align="center">
              <v-col class="display-3" cols="6">100</v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col md="4">
        <v-card class="mx-auto">
          <v-card-title>Hours</v-card-title>
          <v-card-text>
            <v-row align="center">
              <v-col class="display-3" cols="6">12343</v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col md="4">
        <v-card class="mx-auto">
          <v-card-title>Cost</v-card-title>
          <v-card-text>
            <v-row align="center">
              <v-col class="display-3" cols="6">21321343</v-col>
            </v-row>
          </v-card-text>
        </v-card>
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
      <v-col md="6"></v-col>
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
  </v-layout>
</template>

<script>
import _ from "lodash"
import parseISO from "date-fns/parseISO"
import IncidentApi from "@/incident/api"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
export default {
  name: "IncidentDashboard",

  components: {
    IncidentTypeBarChartCard,
    IncidentResolveTimeCard,
    IncidentActiveTimeCard,
    IncidentCostBarChartCard,
    IncidentPriorityBarChartCard
  },

  data() {
    return {
      tab: null,
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
    IncidentApi.getAll({ itemsPerPage: 100, sortBy: ["created_at"], descending: [true] }).then(
      response => {
        this.items = _.sortBy(response.data.items, "created_at")
        this.loading = false
      }
    )
  }
}
</script>
