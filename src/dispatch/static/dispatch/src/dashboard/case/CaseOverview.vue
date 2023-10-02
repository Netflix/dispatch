<template>
  <v-container fluid>
    <!-- <cases-drill-down-sheet -->
    <!--   :show="showDrillDown" -->
    <!--   :items="detailItems" -->
    <!--   @close="showDrillDown = false" -->
    <!-- /> -->
    <v-row>
      <v-col class="d-flex justify-start" cols="12" sm="6">
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-col>
      <v-col class="d-flex justify-end" cols="12" sm="6">
        <case-dialog-filter
          @update="update"
          @loading="setLoading"
          :projects="defaultUserProjects"
        />
      </v-col>
    </v-row>
    <v-row>
      <!-- Widgets Start -->
      <v-col cols="12" sm="6" lg="3">
        <stat-widget icon="mdi-domain" :title="toNumberString(totalCases)" sup-title="Cases" />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-domain"
          :title="toNumberString(totalCasesTriaged)"
          sup-title="Cases Triaged"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-domain"
          :title="toNumberString(totalCasesEscalated)"
          sup-title="Cases Escalated"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-clock"
          :title="toNumberString(totalHours)"
          sup-title="Total Hours (New to Closed)"
        />
      </v-col>
      <!-- Widgets Ends -->
      <!-- Statistics Start -->
      <v-col cols="12" sm="6">
        <case-type-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <case-severity-bar-chart-card
          v-model="groupedItems"
          :loading="loading"
          @details-selected="detailsSelected($event)"
        />
      </v-col>
      <!-- <v-col cols="12" sm="6"> -->
      <!--   <case-priority-bar-chart-card -->
      <!--     v-model="groupedItems" -->
      <!--     :loading="loading" -->
      <!--     @details-selected="detailsSelected($event)" -->
      <!--   /> -->
      <!-- </v-col> -->
      <v-col cols="12" sm="6">
        <case-new-triage-average-time-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12" sm="6">
        <case-triage-escalated-average-time-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12" sm="6">
        <case-escalated-closed-average-time-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12" sm="6">
        <case-new-closed-average-time-card v-model="groupedItems" :loading="loading" />
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

import { toNumberString } from "@/filters"

import CaseDialogFilter from "@/dashboard/case/CaseDialogFilter.vue"
// import CasesDrillDownSheet from "@/dashboard/case/CasesDrillDownSheet.vue"
// import CasePriorityBarChartCard from "@/dashboard/case/CasePriorityBarChartCard.vue"
import CaseEscalatedClosedAverageTimeCard from "@/dashboard/case/CaseEscalatedClosedAverageTimeCard.vue"
import CaseNewClosedAverageTimeCard from "@/dashboard/case/CaseNewClosedAverageTimeCard.vue"
import CaseNewTriageAverageTimeCard from "@/dashboard/case/CaseNewTriageAverageTimeCard.vue"
import CaseSeverityBarChartCard from "@/dashboard/case/CaseSeverityBarChartCard.vue"
import CaseTriageEscalatedAverageTimeCard from "@/dashboard/case/CaseTriageEscalatedAverageTimeCard.vue"
import CaseTypeBarChartCard from "@/dashboard/case/CaseTypeBarChartCard.vue"
import StatWidget from "@/components/StatWidget.vue"

export default {
  name: "CaseDashboard",

  components: {
    CaseDialogFilter,
    // CasePriorityBarChartCard,
    CaseSeverityBarChartCard,
    CaseTypeBarChartCard,
    // CasesDrillDownSheet,
    CaseEscalatedClosedAverageTimeCard,
    CaseNewClosedAverageTimeCard,
    CaseNewTriageAverageTimeCard,
    CaseTriageEscalatedAverageTimeCard,
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
    return { toNumberString }
  },

  methods: {
    update(data) {
      this.items = data.filter(function (item) {
        return (
          !item.case_type.exclude_from_metrics &&
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

    casesByYear() {
      return groupBy(this.items, function (item) {
        return parseISO(item.reported_at).getYear()
      })
    },
    casesByMonth() {
      // add year info if necessary
      if (Object.keys(this.casesByYear).length > 1) {
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
    casesByQuarter() {
      return groupBy(this.items, function (item) {
        return "Q" + Math.floor(parseISO(item.reported_at).getMonth() + 3) / 3
      })
    },
    groupedItems() {
      return this.casesByMonth
    },
    totalCases() {
      return this.items.length
    },
    totalCasesTriaged() {
      return sumBy(this.items, function (item) {
        if (item.triage_at) {
          return 1
        }
      })
    },
    totalCasesEscalated() {
      return sumBy(this.items, function (item) {
        if (item.escalated_at && item.incidents.length > 0) {
          return 1
        }
      })
    },
    totalHours() {
      return sumBy(this.items, function (item) {
        let endTime = new Date().toISOString()
        if (item.closed_at) {
          endTime = item.closed_at
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
