<template>
  <v-container fluid grid-list-xl>
    <v-toolbar dense floating>
      <v-text-field hide-details prepend-icon="search" single-line></v-text-field>

      <v-btn icon>
        <v-icon>my_location</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
    </v-toolbar>
    <v-layout row wrap>
      <!-- Widgets-->
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="domain" title="388" supTitle="Incidents" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="attach_money" title="$141,291" supTitle="Total Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="show_chart" title="$100,000" supTitle="Avg Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="watch_later" title="1300" supTitle="Incident Hours" />
      </v-flex>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-flex lg6 sm6 xs12>
        <incident-type-bar-chart-card v-model="groupedItems" :loading="loading"></incident-type-bar-chart-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-priority-bar-chart-card v-model="groupedItems" :loading="loading"></incident-priority-bar-chart-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-cost-bar-chart-card v-model="groupedItems" :loading="loading"></incident-cost-bar-chart-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-active-time-card v-model="groupedItems" :loading="loading"></incident-active-time-card>
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-resolve-time-card v-model="groupedItems" :loading="loading"></incident-resolve-time-card>
      </v-flex>
      <!-- Statistics Ends -->
    </v-layout>
  </v-container>
</template>

<script>
import _ from "lodash"
import parseISO from "date-fns/parseISO"
import IncidentApi from "@/incident/api"
import StatWidget from "@/components/StatWidget.vue"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
export default {
  name: "IncidentDashboard",

  components: {
    StatWidget,
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
