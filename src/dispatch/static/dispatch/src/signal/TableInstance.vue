<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="text-h5">Signals</div>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card>
          <v-card-title>
            <v-text-field
              v-model="q"
              append-icon="search"
              label="Search"
              single-line
              hide-details
              clearable
            />
          </v-card-title>
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
            <template #item.create_case="{ value }">
              <v-checkbox-btn model="value.signal.create_case" disabled />
            </template>
            <template #item.case="{ value }">
              <case-popover v-if="value" :value="value" />
            </template>
            <template #item.signal="{ value }">
              <signal-popover :value="value" />
            </template>
            <template #item.canary="{ value }">
              <v-checkbox-btn v-model="value.signal.canary" disabled />
            </template>
            <template #item.project.name="{ item, value }">
              <v-chip size="small" :color="item.project.color">
                {{ value }}
              </v-chip>
            </template>
            <template #item.filter_action="{ value }">
              <v-chip
                size="small"
                :color="
                  {
                    snooze: 'blue-accent-4',
                    deduplicate: 'blue-accent-2',
                  }[value]
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
              <raw-signal-viewer :value="item" />
            </template>
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import CasePopover from "@/case/CasePopover.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"
import RouterUtils from "@/router/utils"
import SignalPopover from "@/signal/SignalPopover.vue"

export default {
  name: "SignalInstanceTable",

  components: {
    CasePopover,
    RawSignalViewer,
    SignalPopover,
  },

  data() {
    return {
      headers: [
        { text: "Create Case", value: "create_case", sortable: false },
        { text: "Case", value: "case", sortable: false },
        { text: "Signal Definition", value: "signal", sortable: false },
        { text: "Canary", value: "canary", sortable: false },
        { text: "Filter Action", value: "filter_action", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Created At", value: "created_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
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
      "instanceTable.options.itemsPerPage",
      "instanceTable.options.page",
      "instanceTable.options.q",
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
      (vm) => [vm.q, vm.sortBy, vm.itemsPerPage, vm.descending, vm.created_at, vm.project],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAllInstances()
      }
    )
  },
}
</script>
