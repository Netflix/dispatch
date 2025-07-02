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
    <template #item.signals="{ value }">
      <signal-popover v-if="value && value.length === 1" :value="value[0]" />
      <multi-signal-popover v-else-if="value && value.length > 1" :signals="value" />
      <span v-else>No Signals</span>
    </template>
    <template #item.entities="{ value }">
      <instance-entity-popover :value="value" />
    </template>
    <template #item.expiration="{ value }">
      <span v-if="!value">Never</span>
      <v-tooltip v-else location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(value) }}</span>
        </template>
        <span>{{ formatDate(value) }}</span>
      </v-tooltip>
    </template>
    <template #item.status="{ item }">
      <v-chip size="small" :color="isExpired(item.expiration) ? 'gray' : 'blue-accent-4'">
        {{ isExpired(item.expiration) ? "Expired" : "Active" }}
      </v-chip>
    </template>
    <template #item.data-table-actions="{ item }">
      <!-- todo(amats): doesn't do anything currently. -->
      <v-btn icon variant="text" size="small" @click="editFilter(item)">
        <v-icon>mdi-pencil</v-icon>
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
import MultiSignalPopover from "@/signal/MultiSignalPopover.vue"
import InstanceEntityPopover from "@/signal/InstanceEntityPopover.vue"
import RouterUtils from "@/router/utils"

export default {
  name: "TableFilterSnoozes",

  components: {
    CasePopover,
    SignalPopover,
    MultiSignalPopover,
    InstanceEntityPopover,
  },

  data() {
    return {
      headers: [
        { title: "Status", value: "status", sortable: false },
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: true },
        { title: "Applies to", value: "signals", sortable: false },
        { title: "Expiration", value: "expiration", sortable: true },
        { title: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("signalFilter", [
      "snoozeTable.loading",
      "snoozeTable.options.descending",
      "snoozeTable.options.filters",
      "snoozeTable.options.itemsPerPage",
      "snoozeTable.options.page",
      "snoozeTable.options.sortBy",
      "snoozeTable.rows.items",
      "snoozeTable.rows.total",
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
    ...mapActions("signalFilter", ["getAllSnoozes"]),

    /**
     * Check if a filter is expired based on its expiration date
     * @param expiration: The expiration date of the filter
     */
    isExpired(expiration) {
      return expiration && new Date() >= new Date(expiration)
    },

    /**
     * Open the edit dialog for a filter
     * @param filter: The filter to edit
     */
    editFilter(filter) {
      this.createEditShow(filter)
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }

    this.getAllSnoozes()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAllSnoozes()
      }
    )

    this.$watch(
      (vm) => [vm.sortBy, vm.itemsPerPage, vm.descending, vm.created_at, vm.project, vm.action],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAllSnoozes()
      }
    )
  },
}
</script>
