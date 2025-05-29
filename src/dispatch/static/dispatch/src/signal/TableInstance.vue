<template>
  <v-data-table-server
    :headers="headers"
    :items="items"
    :items-length="total || 0"
    v-model:page="page"
    v-model:items-per-page="itemsPerPage"
    :footer-props="{
      'items-per-page-options': [10, 25, 50, 100],
    }"
    v-model:sort-by="sortBy"
    v-model:sort-desc="descending"
    :loading="loading"
    loading-text="Loading... Please wait"
  >
    <template #item.case="{ value }">
      <case-popover v-if="value" :value="value" />
    </template>
    <template #item.signal="{ value }">
      <signal-popover :value="value" />
    </template>
    <template #item.entities="{ value }">
      <instance-entity-popover :value="value" />
    </template>
    <template #item.signal.filters="{ value }">
      <span
        v-if="this.getSnoozes(value) === 0 && this.getSnoozes(value, (count_expired = true)) === 0"
      >
        No Snoozes Created
      </span>
      <span v-else>
        <v-chip>{{ this.getSnoozes(value) }} Active</v-chip>
        <v-chip>{{ this.getSnoozes(value, (count_expired = true)) }} Expired</v-chip>
      </span>
    </template>
    <template #item.signal.project.display_name="{ item, value }">
      <v-chip size="small" :color="item.signal.project.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.filter_action="{ value }">
      <v-chip
        size="small"
        :color="
          {
            snooze: 'blue-accent-4',
            deduplicate: 'orange-darken-2',
          }[value] || 'green-darken-1'
        "
      >
        {{
          {
            snooze: "Snoozed",
            deduplicate: "Duplicate",
          }[value] || "Not Filtered"
        }}
      </v-chip>
    </template>
    <template #item.created_at="{ value }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(value) }}</span>
        </template>
        <span>{{ formatDate(value) }}</span>
      </v-tooltip>
    </template>
    <template #item.data-table-actions="{ item }">
      <raw-signal-viewer :value="item.raw" />
    </template>
  </v-data-table-server>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import CasePopover from "@/case/CasePopover.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"
import RouterUtils from "@/router/utils"
import SignalPopover from "@/signal/SignalPopover.vue"
import InstanceEntityPopover from "@/signal/InstanceEntityPopover.vue"

export default {
  name: "SignalInstanceTable",

  components: {
    CasePopover,
    RawSignalViewer,
    SignalPopover,
    InstanceEntityPopover,
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

    getSnoozes(signal_filters, count_expired = false) {
      // todo docstring
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
