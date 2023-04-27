<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="headline">Signals</div>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card elevation="0">
          <v-data-table
            :headers="headers"
            :items="items"
            :server-items-length="total"
            :page.sync="page"
            :items-per-page.sync="itemsPerPage"
            :footer-props="{
              'items-per-page-options': [10, 25, 50, 100],
            }"
            :sort-by.sync="sortBy"
            :sort-desc.sync="descending"
            :loading="loading"
            loading-text="Loading... Please wait"
          >
            <template v-slot:item.case="{ item }">
              <case-popover v-if="item.case" v-model="item.case" />
            </template>
            <template v-slot:item.signal="{ item }">
              <signal-popover v-model="item.signal" />
            </template>
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template v-slot:item.filter_action="{ item }">
              <v-chip
                small
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
            <template v-slot:item.created_at="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.created_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.data-table-actions="{ item }">
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
    ...mapFields("route", ["query"]),
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
      ...RouterUtils.deserializeFilters(this.query),
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
