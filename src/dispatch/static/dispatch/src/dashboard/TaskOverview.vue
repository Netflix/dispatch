<template>
  <v-container fluid grid-list-xl>
    <v-layout row wrap>
      <v-flex class="d-flex justify-start" lg6 sm6 xs12>
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-flex>
      <v-flex class="d-flex justify-end" lg6 sm6 xs12>
        <task-dialog-filter
          v-bind="query"
          @update="update"
          @loading="setLoading"
          :projects="defaultUserProjects"
        />
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="playlist_add_check"
          :title="totalTasks | toNumberString"
          sup-title="Tasks"
        />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="watch_later"
          :title="totalHours | toNumberString"
          sup-title="Total Hours"
        />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget icon="people" :title="uniqTeams | toNumberString" sup-title="Unique Teams" />
      </v-flex>
      <v-flex lg3 sm6 xs12>
        <stat-widget
          icon="person"
          :title="uniqAssignees | toNumberString"
          sup-title="Unique Assignees"
        />
      </v-flex>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-flex lg6 sm6 xs12>
        <task-incident-priority-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <task-incident-type-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <v-flex lg6 sm6 xs12>
        <task-active-time-card v-model="groupedItems" :loading="loading" />
      </v-flex>
      <!-- Statistics Ends -->
    </v-layout>
  </v-container>
</template>

<script>
import { groupBy, sumBy, uniq, map } from "lodash"
import { mapFields } from "vuex-map-fields"
import { parseISO } from "date-fns"
import differenceInHours from "date-fns/differenceInHours"

import StatWidget from "@/components/StatWidget.vue"
import TaskActiveTimeCard from "@/task/TaskActiveTimeCard.vue"
import TaskDialogFilter from "@/dashboard/TaskDialogFilter.vue"
import TaskIncidentPriorityBarChartCard from "@/task/TaskIncidentPriorityBarChartCard.vue"
import TaskIncidentTypeBarChartCard from "@/task/TaskIncidentTypeBarChartCard.vue"

export default {
  name: "TaskDashboard",

  components: {
    TaskDialogFilter,
    StatWidget,
    TaskIncidentPriorityBarChartCard,
    TaskIncidentTypeBarChartCard,
    TaskActiveTimeCard,
  },

  props: {
    query: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  data() {
    return {
      tab: null,
      loading: true,
      items: [],
    }
  },

  methods: {
    update(data) {
      this.items = data
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
    ...mapFields("auth", ["currentUser.projects"]),

    tasksByMonth() {
      return groupBy(this.items, function (item) {
        return parseISO(item.created_at).toLocaleString("default", { month: "short" })
      })
    },
    groupedItems() {
      return this.tasksByMonth
    },
    totalTasks() {
      return this.items.length
    },
    uniqTeams() {
      let allTeams = map(this.items, function (item) {
        return map(item.assignees, "team")
      }).flat(1)
      return uniq(allTeams).length
    },
    uniqAssignees() {
      let allAssignees = map(this.items, function (item) {
        return map(item.assignees, "individual.name")
      }).flat(1)
      return uniq(allAssignees).length
    },
    totalHours() {
      return sumBy(this.items, function (item) {
        let endTime = new Date().toISOString()
        if (item.resolved_at) {
          endTime = item.resolved_at
        }
        return differenceInHours(parseISO(endTime), parseISO(item.created_at))
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
