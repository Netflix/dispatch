<template>
  <v-container fluid grid-list-xl>
    <v-layout row wrap>
      <!-- Widgets-->
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="domain" :title="totalIncidents" supTitle="Incidents" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="attach_money" :title="totalCost | dollars" supTitle="Total Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="show_chart" :title="avgCost | dollars" supTitle="Avg Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="watch_later" :title="totalHours" supTitle="Total Hours" />
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
import differenceInHours from "date-fns/differenceInHours"

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
    },
    totalIncidents() {
      return this.items.length
    },
    totalCost() {
      return _.sumBy(this.items, "cost")
    },
    avgCost() {
      return this.totalCost / this.totalIncidents
    },
    totalHours() {
      return _.sumBy(this.items, function(item) {
        let endTime = new Date().toISOString()
        if (item.stable_at) {
          endTime = item.stable_at
        }
        return differenceInHours(parseISO(endTime), parseISO(item.reported_at))
      })
    }
  },

  created() {
    this.loading = true
    // TODO make this reported_at
    IncidentApi.getAll({ itemsPerPage: 10, sortBy: ["reported_at"], descending: [true] }).then(
      response => {
        this.items = _.sortBy(response.data.items, "reported_at")
        this.loading = false
      }
    )
  }
}
</script>
