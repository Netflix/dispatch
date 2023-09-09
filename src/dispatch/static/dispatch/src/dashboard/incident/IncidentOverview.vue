<template>
  <v-container fluid grid-list-xl>
    <incidents-drill-down-sheet v-model="showDrillDown" :items="detailItems" />
    <v-layout row wrap>
      <v-flex class="d-flex justify-start" lg6 sm6 xs12>
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-flex>
      <v-flex class="d-flex justify-end" lg6 sm6 xs12>
        <incident-dialog-filter
          @update="update"
          @loading="setLoading"
          :projects="defaultUserProjects"
        />
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="domain" :title="totalIncidents | toNumberString" sup-title="Incidents" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="watch_later"
          :title="totalResponseHours | toNumberString"
          sup-title="Total Response Hours"
        />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="attach_money"
          :title="totalIncidentsCost | toUSD"
          sup-title="Total Incidents Cost"
        />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="show_chart"
          :title="averageIncidentCost | toUSD"
          sup-title="Average Cost Per Incident"
        />
      </v-flex>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-flex lg12 sm12 xs12>
        <incident-type-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-severity-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-priority-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-mean-response-time-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-cost-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-forecast-card />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-reporters-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-commanders-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-participants-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-participants-team-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-heatmap-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <incident-tags-treemap-card
          v-model="items"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <!-- Statistics Ends -->
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { groupBy, sumBy } from "lodash"
import { parseISO } from "date-fns"

import differenceInHours from "date-fns/differenceInHours"

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
    ...mapFields("route", ["query.project"]),
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
