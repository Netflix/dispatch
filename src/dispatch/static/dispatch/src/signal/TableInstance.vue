<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="text-h5">Signals</div>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card elevation="0">
          <v-data-table
            :headers="headers"
            :items="items"
            :server-items-length="total"
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
            <template #item.case="{ item }">
              <case-popover v-if="item.case" v-model="item.case" />
            </template>
            <template #item.signal="{ item }">
              <signal-popover v-model="item.signal" />
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.filter_action="{ item }">
              <v-chip
                size="small"
                text-color="white"
                :color="
                  item.filter_action === 'snooze'
                    ? 'blue-accent-4'
                    : item.filter_action === 'deduplicate'
                    ? 'blue-accent-2'
                    : ''
                "
              >
                {{
                  item.filter_action === "snooze"
                    ? "Snoozed"
                    : item.filter_action === "deduplicate"
                    ? "Duplicate"
                    : "Not Filtered"
                }}
              </v-chip>
            </template>
            <template #item.created_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ formatRelativeDate(item.created_at) }}</span>
                </template>
                <span>{{ formatDate(item.created_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.data-table-actions="{ item }">
              <raw-signal-viewer v-model="item.raw" />
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import RouterUtils from "@/router/utils"
import SignalPopover from "@/signal/SignalPopover.vue"
import CasePopover from "@/case/CasePopover.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"

export default {
  name: "SignalInstanceTable",

  components: {
    SignalPopover,
    CasePopover,
    RawSignalViewer,
  },

  data() {
    return {
      headers: [
        { text: "Case", value: "case", sortable: false },
        { text: "Signal", value: "signal", sortable: false },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Filter Action", value: "filter_action", sortable: true },
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
