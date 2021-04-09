<template>
  <v-container fluid grid-list-xl>
    <v-layout row wrap>
      <v-flex class="d-flex justify-start" lg6 sm6 xs12>
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-flex>
      <v-flex class="d-flex justify-end" lg6 sm6 xs12>
        <dialog-filter :project="project" @update="update" @loading="setLoading" />
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="domain" :title="totalIncidents | toNumberString" sup-title="Incidents" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="attach_money" :title="totalCost | toUSD" sup-title="Total Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="show_chart" :title="avgCost | toUSD" sup-title="Avg Cost" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="watch_later"
          :title="totalHours | toNumberString"
          sup-title="Total Hours"
        />
      </v-flex>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-flex lg6 sm6 xs12>
        <incident-type-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-priority-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-heatmap-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-cost-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-forecast-card />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-active-time-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-resolve-time-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-primary-location-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-primary-team-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-tags-treemap-card v-model="items" :loading="loading" />
      </v-flex>
      <!-- Statistics Ends -->
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { groupBy, sumBy, filter } from "lodash"
import differenceInHours from "date-fns/differenceInHours"
import { parseISO } from "date-fns"

import DialogFilter from "@/dashboard/DialogFilter.vue"
import StatWidget from "@/components/StatWidget.vue"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
import IncidentForecastCard from "@/incident/IncidentForecastCard.vue"
import IncidentHeatmapCard from "@/incident/IncidentHeatmapCard.vue"
import IncidentPrimaryLocationBarChartCard from "@/incident/IncidentPrimaryLocationBarChartCard.vue"
import IncidentPrimaryTeamBarChartCard from "@/incident/IncidentPrimaryTeamBarChartCard.vue"
import IncidentTagsTreemapCard from "@/incident/IncidentTagsTreemapCard.vue"
export default {
  name: "IncidentDashboard",

  components: {
    DialogFilter,
    StatWidget,
    IncidentHeatmapCard,
    IncidentTypeBarChartCard,
    IncidentResolveTimeCard,
    IncidentActiveTimeCard,
    IncidentCostBarChartCard,
    IncidentPriorityBarChartCard,
    IncidentForecastCard,
    IncidentPrimaryLocationBarChartCard,
    IncidentPrimaryTeamBarChartCard,
    IncidentTagsTreemapCard,
  },

  data() {
    return {
      tab: null,
      loading: "error",
      items: [],
    }
  },

  methods: {
    update(data) {
      this.items = filter(data, function (item) {
        return !item.incident_type.exclude_from_metrics && !item.duplicates.length
      })
    },
    setLoading(data) {
      this.loading = data
    },
    copyView: function () {
      let store = this.$store
      this.$copyText(window.location).then(
        function () {
          store.commit(
            "notification_backend/addBeNotification",
            {
              text: "View copied to clipboard.",
            },
            { root: true }
          )
        },
        function () {
          store.commit(
            "notification_backend/addBeNotification",
            {
              text: "Failed to copy view to clipboard.",
              color: "red",
            },
            { root: true }
          )
        }
      )
    },
  },

  computed: {
    incidentsByYear() {
      return groupBy(this.items, function (item) {
        return parseISO(item.reported_at).getYear()
      })
    },
    incidentsByMonth() {
      return groupBy(this.items, function (item) {
        return parseISO(item.reported_at).toLocaleString("default", { month: "short" })
      })
    },
    incidentsByQuarter() {
      return groupBy(this.items, function (item) {
        return "Q" + Math.floor(parseISO(item.reported_at).getMonth() + 3) / 3
      })
    },
    groupedItems() {
      return this.incidentsByMonth
    },
    totalIncidents() {
      return this.items.length
    },
    totalCost() {
      return sumBy(this.items, "total_cost")
    },
    avgCost() {
      return this.totalCost / this.totalIncidents
    },
    totalHours() {
      return sumBy(this.items, function (item) {
        let endTime = new Date().toISOString()
        if (item.stable_at) {
          endTime = item.stable_at
        }
        return differenceInHours(parseISO(endTime), parseISO(item.reported_at))
      })
    },
    ...mapFields("route", ["query.project"]),
  },
}
</script>
