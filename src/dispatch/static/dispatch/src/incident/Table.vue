<template>
  <v-container fluid>
    <div v-if="showEditSheet">
      <router-view />
    </div>
    <v-row no-gutters>
      <new-sheet />
      <delete-dialog />
      <report-dialog />
      <workflow-run-modal />
      <v-col>
        <div class="headline">Incidents</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
        <table-export-dialog />
        <v-btn color="info" class="ml-2" @click="showNewSheet()"> New </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card elevation="0">
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
          <v-data-table
            :headers="headers"
            :items="items"
            :server-items-length="total"
            :page.sync="page"
            :items-per-page.sync="itemsPerPage"
            :sort-by.sync="sortBy"
            :sort-desc.sync="descending"
            :loading="loading"
            data-testid="incident-data-table"
            v-model="selected"
            loading-text="Loading... Please wait"
            show-select
          >
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template v-slot:item.incident_severity.name="{ item }">
              <incident-severity :severity="item.incident_severity.name" />
            </template>
            <template v-slot:item.incident_priority.name="{ item }">
              <incident-priority :priority="item.incident_priority.name" />
            </template>
            <template v-slot:item.status="{ item }">
              <incident-status :status="item.status" :id="item.id" />
            </template>
            <template v-slot:item.incident_costs="{ item }">
              <incident-cost-card :incident-costs="item.incident_costs" />
            </template>
            <template v-slot:item.commander="{ item }">
              <incident-participant :participant="item.commander" />
            </template>
            <template v-slot:item.reported_at="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.reported_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.reported_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.closed_at="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.closed_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.closed_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.data-table-actions="{ item }">
              <v-menu bottom left>
                <template v-slot:activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item
                    data-testid="incident-table-edit"
                    :to="{
                      name: 'IncidentTableEdit',
                      params: { name: item.name },
                    }"
                  >
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="showReportDialog(item)" :disabled="item.status == 'Closed'">
                    <v-list-item-title>Create Report</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="showRun({ type: 'incident', data: item })" :disabled="item.status == 'Closed'">
                    <v-list-item-title>Run Workflow</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="showDeleteDialog(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    <bulk-edit-sheet />
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import BulkEditSheet from "@/incident/BulkEditSheet.vue"
import DeleteDialog from "@/incident/DeleteDialog.vue"
import IncidentCostCard from "@/incident_cost/IncidentCostCard.vue"
import IncidentParticipant from "@/incident/Participant.vue"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentSeverity from "@/incident/severity/IncidentSeverity.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"
import NewSheet from "@/incident/NewSheet.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"
import ReportDialog from "@/incident/ReportDialog.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/incident/TableExportDialog.vue"
import TableFilterDialog from "@/incident/TableFilterDialog.vue"

export default {
  name: "IncidentTable",

  components: {
    BulkEditSheet,
    DeleteDialog,
    IncidentCostCard,
    IncidentParticipant,
    IncidentPriority,
    IncidentSeverity,
    IncidentStatus,
    NewSheet,
    ReportDialog,
    WorkflowRunModal,
    TableExportDialog,
    TableFilterDialog,
  },

  props: {
    name: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status" },
        { text: "Type", value: "incident_type.name" },
        { text: "Severity", value: "incident_severity.name", width: "10%" },
        { text: "Priority", value: "incident_priority.name", width: "10%" },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Commander", value: "commander", sortable: false },
        { text: "Cost", value: "incident_costs", sortable: false },
        { text: "Reported At", value: "reported_at" },
        { text: "Closed At", value: "closed_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.loading",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.commander",
      "table.options.filters.incident_priority",
      "table.options.filters.incident_severity",
      "table.options.filters.incident_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.reporter",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.selected",
      "table.rows.total",
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
    ...mapActions("incident", ["getAll", "showNewSheet", "showDeleteDialog", "showReportDialog"]),
    ...mapActions("workflow", ["showRun"]),
  },

  watch: {
    $route: {
      immediate: true,
      handler: function (newVal) {
        this.showEditSheet = newVal.meta && newVal.meta.showEditSheet
      },
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.query),
      project: this.defaultUserProjects,
    }

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [
        vm.descending,
        vm.incident_priority,
        vm.incident_severity,
        vm.incident_type,
        vm.itemsPerPage,
        vm.project,
        vm.q,
        vm.reported_at.end,
        vm.reported_at.start,
        vm.sortBy,
        vm.status,
        vm.tag,
        vm.tag_type,
      ],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAll()
      }
    )
  },
}
</script>
