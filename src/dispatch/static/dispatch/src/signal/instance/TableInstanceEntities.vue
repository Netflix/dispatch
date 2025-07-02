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
    <template #item.project.display_name="{ item, value }">
      <v-chip size="small" :color="item.project.color">
        {{ value }}
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
    <template #item.instanceStats="{ value }">
      <span>
        <v-chip color="red-darken-1" size="small">
          {{ value.num_signal_instances_alerted }} events
        </v-chip>
        <v-chip color="blue-accent-4" size="small">
          {{ value.num_signal_instances_snoozed }} filtered
        </v-chip>
      </span>
    </template>
    <!-- todo(amats): duplication issue here -->
    <template #item.snoozeStats="{ value }">
      <span>
        <v-chip size="small">{{ value.num_snoozes_active }} Active</v-chip>
        <v-chip size="small">{{ value.num_snoozes_expired }} Expired</v-chip>
      </span>
    </template>
  </v-data-table-server>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import RouterUtils from "@/router/utils"

export default {
  name: "TableInstanceEntities",

  data() {
    return {
      headers: [
        { title: "Type", value: "entity_type.name", sortable: true },
        { title: "Value", value: "value", sortable: true },
        { title: "Description", value: "entity_type.description", sortable: false },
        { title: "Signal Triggers", value: "instanceStats", sortable: false },
        { title: "Snooze Filters", value: "snoozeStats", sortable: false },
        { title: "Project", value: "project.display_name", sortable: true },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("signal", [
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
    ...mapActions("signal", ["getAllEntities"]),
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }

    this.getAllEntities()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAllEntities()
      }
    )

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
