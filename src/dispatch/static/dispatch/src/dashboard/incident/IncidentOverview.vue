<template>
  <v-container fluid>
    <incidents-drill-down-sheet v-model="showDrillDown" :items="detailItems" />
    <v-row>
      <v-col class="d-flex justify-start" cols="12" sm="6">
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-col>
      <v-col class="d-flex justify-end" cols="12" sm="6">
        <incident-dialog-filter
          @update="update"
          @loading="setLoading"
          :projects="defaultUserProjects"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-domain"
          :title="toNumberString(totalIncidents)"
          sup-title="Incidents"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-clock"
          :title="toNumberString(totalResponseHours)"
          sup-title="Total Response Hours"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-currency-usd"
          :title="toUSD(totalIncidentsCost)"
          sup-title="Total Incidents Cost"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-chart-line-variant"
          :title="toUSD(averageIncidentCost)"
          sup-title="Average Cost Per Incident"
        />
      </v-col>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-col cols="12">
        <incident-type-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-severity-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-priority-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-mean-response-time-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-cost-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12">
        <incident-forecast-card />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-reporters-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-commanders-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-participants-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-participants-team-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-heatmap-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <incident-tags-treemap-card
          v-model="items"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <!-- Statistics Ends -->
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { groupBy, sumBy } from "lodash"
import parseISO from "date-fns/parseISO"
import differenceInHours from "date-fns/differenceInHours"

import { toNumberString, toUSD } from "@/filters"

import IncidentCommandersLocationBarChartCard from "@/dashboard/incident/IncidentCommandersLocationBarChartCard.vue"
import IncidentCostBarChartCard from "@/dashboard/incident/IncidentCostBarChartCard.vue"
import IncidentDialogFilter from "@/dashboard/incident/IncidentDialogFilter.vue"
import IncidentForecastCard from "@/dashboard/incident/IncidentForecastCard.vue"
import IncidentHeatmapCard from "@/dashboard/incident/IncidentHeatmapCard.vue"
import IncidentMeanResponseTimeCard from "@/dashboard/incident/IncidentMeanResponseTimeCard.vue"
import IncidentParticipantsLocationBarChartCard from "@/dashboard/incident/IncidentParticipantsLocationBarChartCard.vue"
import IncidentParticipantsTeamBarChartCard from "@/dashboard/incident/IncidentParticipantsTeamBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/dashboard/incident/IncidentPriorityBarChartCard.vue"
import IncidentReportersLocationBarChartCard from "@/dashboard/incident/IncidentReportersLocationBarChartCard.vue"
import IncidentSeverityBarChartCard from "@/dashboard/incident/IncidentSeverityBarChartCard.vue"
import IncidentTagsTreemapCard from "@/dashboard/incident/IncidentTagsTreemapCard.vue"
import IncidentTypeBarChartCard from "@/dashboard/incident/IncidentTypeBarChartCard.vue"
import IncidentsDrillDownSheet from "@/dashboard/incident/IncidentsDrillDownSheet.vue"
import StatWidget from "@/components/StatWidget.vue"

export default {
  name: "IncidentDashboard",

  components: {
    IncidentCommandersLocationBarChartCard,
    IncidentCostBarChartCard,
    IncidentDialogFilter,
    IncidentForecastCard,
    IncidentHeatmapCard,
    IncidentMeanResponseTimeCard,
    IncidentParticipantsLocationBarChartCard,
    IncidentParticipantsTeamBarChartCard,
    IncidentPriorityBarChartCard,
    IncidentReportersLocationBarChartCard,
    IncidentSeverityBarChartCard,
    IncidentTagsTreemapCard,
    IncidentTypeBarChartCard,
    IncidentsDrillDownSheet,
    StatWidget,
  },

  data() {
    return {
      tab: null,
      loading: "error",
      items: [],
      detailItems: [],
      showDrillDown: false,
    }
  },

  setup() {
    return { toNumberString, toUSD }
  },

  methods: {
    update(data) {
      this.items = data.filter(function (item) {
        return (
          !item.incident_type.exclude_from_metrics &&
          !item.duplicates.filter((d) => data.includes(d)).length
        )
      })
    },
    detailsSelected(event) {
      this.detailItems = event
      this.showDrillDown = true
    },
    setLoading(data) {
      this.loading = data
    },
    copyView: function () {
      let store = this.$store
      navigator.clipboard.writeText(window.location).then(
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
    ...mapFields("auth", ["currentUser.projects"]),

    incidentsByYear() {
      return groupBy(this.items, function (item) {
        return parseISO(item.reported_at).getYear()
      })
    },
    incidentsByMonth() {
      // add year info if necessary
      if (Object.keys(this.incidentsByYear).length > 1) {
        return groupBy(this.items, function (item) {
          return parseISO(item.reported_at).toLocaleString("default", {
            month: "short",
            year: "numeric",
          })
        })
      } else {
        return groupBy(this.items, function (item) {
          return parseISO(item.reported_at).toLocaleString("default", {
            month: "short",
          })
        })
      }
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
    totalIncidentsCost() {
      return sumBy(this.items, "total_cost")
    },
    averageIncidentCost() {
      return this.totalIncidentsCost / this.totalIncidents
    },
    totalResponseHours() {
      return sumBy(this.items, function (item) {
        let endTime = new Date().toISOString()
        if (item.stable_at) {
          endTime = item.stable_at
        }
        return differenceInHours(parseISO(endTime), parseISO(item.reported_at))
      })
    },
    defaultUserProjects: {
      get() {
        let d = null
        if (this.projects) {
          let d = this.projects.filter((v) => v.default === true)
          return d.map((v) => v.project)
        }
        return d
      },
    },
  },
}
</script>
