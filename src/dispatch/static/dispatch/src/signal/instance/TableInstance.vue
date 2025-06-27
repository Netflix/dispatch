<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="text-h5">Signals</div>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-3" align="center">
      <v-col cols="auto" class="pr-4"><div class="text">Group by:</div></v-col>
      <v-col cols="auto" class="pr-4">
        <v-btn
          :class="activeView === 'triggers' ? 'selectedViewButton' : 'viewButton'"
          @click="setActiveView('triggers')"
        >
          <v-icon>mdi-broadcast</v-icon>
          <div class="pl-1">Triggers</div>
        </v-btn>
      </v-col>
      <!--      todo (amats) we should have routes to allow navigation to a certain tab via link-->
      <v-col cols="auto" class="pr-4">
        <v-btn
          :class="activeView === 'entities' ? 'selectedViewButton' : 'viewButton'"
          @click="setActiveView('entities')"
        >
          <v-icon>mdi-cube-outline</v-icon>
          <div class="pl-1">Entities</div>
        </v-btn>
      </v-col>
      <v-col cols="auto" class="pr-4">
        <v-btn
          :class="activeView === 'snoozes' ? 'selectedViewButton' : 'viewButton'"
          @click="setActiveView('snoozes')"
        >
          <v-icon>mdi-bell-off</v-icon>
          <div class="pl-1">Snoozes</div>
        </v-btn>
      </v-col>
      <v-col class="text-right" style="padding-right: 4px">
        <table-filter-dialog />
      </v-col>
    </v-row>
    <table-instance-triggers v-if="activeView === 'triggers'" />
    <table-instance-entities v-if="activeView === 'entities'" />
    <table-instance-snoozes v-if="activeView === 'snoozes'" />
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import RouterUtils from "@/router/utils"
import TableFilterDialog from "@/signal/TableFilterDialog.vue"
import TableInstanceTriggers from "@/signal/instance/TableInstanceTriggers.vue"
import TableInstanceEntities from "@/signal/instance/TableInstanceEntities.vue"
import TableInstanceSnoozes from "@/signal/instance/TableInstanceSnoozes.vue"

export default {
  name: "SignalInstanceTable",

  components: {
    TableFilterDialog,
    TableInstanceTriggers,
    TableInstanceEntities,
    TableInstanceSnoozes,
  },

  data() {
    return {
      activeView: "triggers",
      headers: [
        { title: "Case", value: "case", sortable: false },
        { title: "Status", value: "filter_action", sortable: true },
        { title: "Signal Definition", value: "signal", sortable: false },
        { title: "Entities", value: "entities", sortable: true },
        { title: "Snoozes", value: "signal.filters", sortable: false },
        { title: "Project", value: "signal.project.display_name", sortable: true },
        { title: "Created At", value: "created_at" },
        { title: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("signal", [
      "instanceTable.loading",
      "instanceTable.options.descending",
      "instanceTable.options.filters",
      "instanceTable.options.filters.signal",
      "instanceTable.options.itemsPerPage",
      "instanceTable.options.page",
      // "instanceTable.options.q",
      "instanceTable.options.sortBy",
      "instanceTable.rows.items",
      "instanceTable.rows.total",
    ]),
    ...mapFields("auth", ["currentUser.projects"]),

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

  methods: {
    ...mapActions("signal", ["getAllInstances"]),

    /**
     * Set the active view and update the UI accordingly.
     * @param view: The view to set as active ('triggers', 'entities', or 'snoozes').
     */
    setActiveView(view) {
      this.activeView = view
    },

    /**
     * Count the snooze filters for a given signal definition. Counts all
     * active snoozes by default, with the option to count expired snoozes instead.
     * @param signal_filters: The definition's filters.
     * @param count_expired: If true, count expired snoozes instead of active ones.
     */
    getSnoozes(signal_filters, count_expired = false) {
      let snoozes = 0
      for (let filter of signal_filters) {
        if (filter.action === "snooze") {
          let filter_is_expired = filter.expiration && new Date() >= new Date(filter.expiration)
          if (!count_expired && !filter_is_expired) {
            snoozes++
          } else if (count_expired && filter_is_expired) {
            snoozes++
          }
        }
      }
      return snoozes
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }

    this.getAllInstances()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAllInstances()
      }
    )

    this.$watch(
      (vm) => [
        // vm.q,
        vm.sortBy,
        vm.itemsPerPage,
        vm.descending,
        vm.created_at,
        vm.project,
        vm.signal,
      ],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAllInstances()
      }
    )
  },
}
</script>

<style>
@import "@/styles/index.scss";

.viewButton {
  background-color: rgb(var(--v-theme-background2));
  color: rgb(var(--v-theme-anchor));
  box-shadow: 0 0 0 0;
}

.selectedViewButton {
  background-color: rgb(var(--v-theme-gray7));
  color: rgb(var(--v-theme-gray0));
  box-shadow: 0 0 0 0;
}
</style>
