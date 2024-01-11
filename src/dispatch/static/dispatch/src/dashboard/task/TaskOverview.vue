<template>
  <v-container fluid>
    <v-row>
      <v-col class="d-flex justify-start" cols="12" sm="6">
        <v-btn color="info" @click="copyView"> Share View </v-btn>
      </v-col>
      <v-col class="d-flex justify-end" cols="12" sm="6">
        <task-dialog-filter
          v-bind="query"
          @update="update"
          @loading="setLoading"
          :projects="defaultUserProjects"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-playlist-check"
          :title="toNumberString(totalTasks)"
          sup-title="Tasks"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget icon="mdi-clock" :title="toNumberString(totalHours)" sup-title="Total Hours" />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-account-multiple"
          :title="toNumberString(uniqTeams)"
          sup-title="Unique Teams"
        />
      </v-col>
      <v-col cols="12" sm="6" lg="3">
        <stat-widget
          icon="mdi-account"
          :title="toNumberString(uniqAssignees)"
          sup-title="Unique Assignees"
        />
      </v-col>
      <!-- Widgets Ends -->
      <!-- Statistics -->
      <v-col cols="12" sm="6">
        <task-incident-priority-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12" sm="6">
        <task-incident-type-bar-chart-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <v-col cols="12" sm="6">
        <task-active-time-card v-model="groupedItems" :loading="loading" />
      </v-col>
      <!-- Statistics Ends -->
    </v-row>
  </v-container>
</template>

<script>
import { groupBy, sumBy, uniq, map } from "lodash"
import { mapFields } from "vuex-map-fields"
import parseISO from "date-fns/parseISO"
import differenceInHours from "date-fns/differenceInHours"

import { toNumberString } from "@/filters"

import StatWidget from "@/components/StatWidget.vue"
import TaskActiveTimeCard from "@/task/TaskActiveTimeCard.vue"
import TaskDialogFilter from "@/dashboard/task/TaskDialogFilter.vue"
import TaskIncidentPriorityBarChartCard from "@/task/TaskIncidentPriorityBarChartCard.vue"
import TaskIncidentTypeBarChartCard from "@/task/TaskIncidentTypeBarChartCard.vue"

export default {
  name: "TaskDashboard",

  components: {
    StatWidget,
    TaskActiveTimeCard,
    TaskDialogFilter,
    TaskIncidentPriorityBarChartCard,
    TaskIncidentTypeBarChartCard,
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

  setup() {
    return { toNumberString }
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
