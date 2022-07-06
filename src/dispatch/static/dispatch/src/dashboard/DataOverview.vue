<template>
  <v-container fluid grid-list-xl>
    <v-layout row wrap>
      <v-flex class="d-flex justify-start" lg6 sm6 xs12>
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-flex>
      <v-flex class="d-flex justify-end" lg6 sm6 xs12>
        <dialog-filter
          @filterOptions="setFilterOptions"
          @update="update"
          @loading="setLoading"
          :projects="defaultUserProjects"
        />
      </v-flex>
    </v-layout>
    <v-row>
      <v-col>
        <stat-widget
          icon="mdi-database"
          :title="totalSources | toNumberString"
          sup-title="Sources"
        />
      </v-col>
      <v-col>
        <stat-widget
          icon="mdi-database-search"
          :title="totalSourceCost | toNumberString"
          sup-title="Queries"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col> <div class="text-h5">Sources</div> </v-col>
    </v-row>
    <v-row>
      <v-col>
        <stat-widget
          icon="mdi-currency-usd"
          :title="totalSourceCost | toNumberString"
          sup-title="Total Cost"
        />
      </v-col>
      <v-col>
        <stat-widget
          icon="mdi-currency-usd"
          :title="avgSourceCost | toNumberString"
          sup-title="Average Cost"
        />
      </v-col>
      <v-col>
        <stat-widget
          icon="mdi-clock"
          :title="avgSourceDelay | toNumberString"
          sup-title="Average Delay (hours)"
        />
      </v-col>
      <v-col>
        <stat-widget
          icon="mdi-safe"
          :title="avgSourceRetention | toNumberString"
          sup-title="Average Retention (days)"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <source-top-5-cost-table-card :loading="loading" v-model="items" />
      </v-col>
      <v-col>
        <source-top-5-incident-table-card :loading="loading" v-model="items" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { filter, sumBy } from "lodash"
import { mapFields } from "vuex-map-fields"

import DialogFilter from "@/dashboard/DataDialogFilter.vue"
import SourceTop5CostTableCard from "@/data/source/SourceTop5CostTableCard.vue"
import SourceTop5IncidentTableCard from "@/data/source/SourceTop5IncidentTableCard.vue"
import StatWidget from "@/components/StatWidget.vue"

export default {
  name: "DataDashboard",

  components: {
    DialogFilter,
    StatWidget,
    SourceTop5CostTableCard,
    SourceTop5IncidentTableCard,
  },

  data() {
    return {
      tab: null,
      loading: "error",
      items: [],
      detailItems: [],
      filterOptions: null,
    }
  },

  methods: {
    update(data) {
      this.items = filter(data, function (item) {
        return item
      })
    },
    setLoading(data) {
      this.loading = data
    },
    setFilterOptions(data) {
      this.filterOptions = data
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

    totalSources() {
      return this.items.length
    },
    totalSourceCost() {
      return this.items.length
    },
    avgSourceRetention() {
      return (
        sumBy(this.items, function (item) {
          return item.retention
        }) / this.totalSources
      )
    },
    avgSourceDelay() {
      return (
        sumBy(this.items, function (item) {
          return item.delay
        }) / this.totalSources
      )
    },
    avgSourceCost() {
      return (
        sumBy(this.items, function (item) {
          return item.cost
        }) / this.totalSources
      )
    },
    avgSourceDailyVolume() {
      return (
        sumBy(this.items, function (item) {
          return item.volume
        }) / this.totalSources
      )
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
