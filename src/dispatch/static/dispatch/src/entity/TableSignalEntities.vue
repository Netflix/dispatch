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
      <span v-if="getSnoozes(value) === 0 && getSnoozes(value, true) === 0">
        No Snoozes Created
      </span>
      <span v-else>
        <v-chip>{{ getSnoozes(value) }} Active</v-chip>
        <v-chip>{{ getSnoozes(value, true) }} Expired</v-chip>
      </span>
    </template>
    <template #item.signal.project.display_name="{ item, value }">
      <v-chip size="small" :color="item.signal.project.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.status="{ value }">
      <v-chip
        size="small"
        :color="
          {
            active: 'green-darken-1',
            inactive: 'gray',
          }[value] || 'blue-accent-4'
        "
      >
        {{ value || "Unknown" }}
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
      <v-btn icon variant="text" size="small" @click="viewEntity(item)">
        <v-icon>mdi-eye</v-icon>
      </v-btn>
    </template>
  </v-data-table-server>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import CasePopover from "@/case/CasePopover.vue"
import SignalPopover from "@/signal/SignalPopover.vue"
import InstanceEntityPopover from "@/signal/InstanceEntityPopover.vue"
import RouterUtils from "@/router/utils"

export default {
  name: "TableSignalEntities",

  components: {
    CasePopover,
    SignalPopover,
    InstanceEntityPopover,
  },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Status", value: "status", sortable: true },
        { title: "Description", value: "description", sortable: true },
        { title: "Signal", value: "signal", sortable: false },
        { title: "Entities", value: "entities", sortable: true },
        { title: "Project", value: "signal.project", sortable: true },
        { title: "Created At", value: "created_at" },
        { title: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("entity", [
      "signalEntityTable.loading",
      "signalEntityTable.options.descending",
      "signalEntityTable.options.filters",
      "signalEntityTable.options.itemsPerPage",
      "signalEntityTable.options.page",
      "signalEntityTable.options.sortBy",
      "signalEntityTable.rows.items",
      "signalEntityTable.rows.total",
    ]),
    ...mapFields("auth", ["currentUser.projects"]),

    defaultUserProjects: {
      get() {
        let d = null
        if (this.projects) {
          d = this.projects.filter((v) => v.default === true)
          return d.map((v) => v.project)
        }
        return d
      },
    },
  },

  methods: {
    ...mapActions("entity", ["getAllEntities"]),

    // todo(amats) - unnecessary functions
    /**
     * Count the snooze filters for a given signal definition. Counts all
     * active snoozes by default, with the option to count expired snoozes instead.
     * @param signal_filters: The definition's filters.
     * @param count_expired: If true, count expired snoozes instead of active ones.
     */
    getSnoozes(signal_filters, count_expired = false) {
      if (!signal_filters) return 0

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

    /**
     * View entity details
     * @param entity: The entity to view
     */
    viewEntity(entity) {
      this.$router.push({ name: "EntityDetail", params: { id: entity.id } })
    },
  },

  created() {
    // Set up filters with default user projects
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }

    // Initial data fetch
    this.getAllEntities()

    // Watch for page changes
    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAllEntities()
      }
    )

    // Watch for filter changes
    this.$watch(
      (vm) => [vm.sortBy, vm.itemsPerPage, vm.descending, vm.created_at, vm.project],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAllEntities()
      }
    )
  },
}
</script>
