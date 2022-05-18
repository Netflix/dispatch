<template>
  <v-container fluid grid-list-xl>
    <incidents-drill-down-sheet
      :show="showDrillDown"
      :items="detailItems"
      @close="showDrillDown = false"
    />
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
        <incident-type-bar-chart-card
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
        <incident-heatmap-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
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
        <incident-reporters-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-commanders-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-participants-location-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg12 sm12 xs12>
        <incident-participants-team-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @detailsSelected="detailsSelected($event)"
        />
      </v-flex>
      <v-flex lg12 sm12 xs12>
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
import { groupBy, sumBy, filter } from "lodash"
import { parseISO } from "date-fns"
import differenceInHours from "date-fns/differenceInHours"

import IncidentActiveTimeCard from "@/incident/IncidentActiveTimeCard.vue"
import IncidentCommandersLocationBarChartCard from "@/incident/IncidentCommandersLocationBarChartCard.vue"
import IncidentCostBarChartCard from "@/incident/IncidentCostBarChartCard.vue"
import IncidentDialogFilter from "@/dashboard/IncidentDialogFilter.vue"
import IncidentForecastCard from "@/incident/IncidentForecastCard.vue"
import IncidentHeatmapCard from "@/incident/IncidentHeatmapCard.vue"
import IncidentParticipantsLocationBarChartCard from "@/incident/IncidentParticipantsLocationBarChartCard.vue"
import IncidentParticipantsTeamBarChartCard from "@/incident/IncidentParticipantsTeamBarChartCard.vue"
import IncidentPriorityBarChartCard from "@/incident/IncidentPriorityBarChartCard.vue"
import IncidentReportersLocationBarChartCard from "@/incident/IncidentReportersLocationBarChartCard.vue"
import IncidentResolveTimeCard from "@/incident/IncidentResolveTimeCard.vue"
import IncidentTagsTreemapCard from "@/incident/IncidentTagsTreemapCard.vue"
import IncidentTypeBarChartCard from "@/incident/IncidentTypeBarChartCard.vue"
import IncidentsDrillDownSheet from "@/dashboard/IncidentsDrillDownSheet.vue"
import StatWidget from "@/components/StatWidget.vue"

export default {
  name: "IncidentDashboard",

  components: {
    IncidentActiveTimeCard,
    IncidentCommandersLocationBarChartCard,
    IncidentCostBarChartCard,
    IncidentDialogFilter,
    IncidentForecastCard,
    IncidentHeatmapCard,
    IncidentParticipantsLocationBarChartCard,
    IncidentParticipantsTeamBarChartCard,
    IncidentPriorityBarChartCard,
    IncidentReportersLocationBarChartCard,
    IncidentResolveTimeCard,
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
      this.items = filter(data, function (item) {
        return !item.incident_type.exclude_from_metrics && !item.duplicates.length
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
