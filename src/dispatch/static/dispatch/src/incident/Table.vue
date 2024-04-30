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
        <div class="text-h5">Incidents</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
        <table-export-dialog />
        <v-btn nav variant="flat" color="error" :to="{ name: 'report' }" class="ml-2" hide-details>
          <v-icon start color="white">mdi-fire</v-icon>
          <span class="text-uppercase text-body-2 font-weight-bold">Report incident</span>
        </v-btn>
        <v-btn
          v-if="userAdminOrAbove(current_user_role)"
          color="info"
          class="ml-2"
          @click="showNewSheet()"
        >
          New
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card variant="flat">
          <v-card-title>
            <v-text-field
              v-model="q"
              append-inner-icon="mdi-magnify"
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
            data-testid="incident-data-table"
            v-model="selected"
            loading-text="Loading... Please wait"
            show-select
            return-object
            @click:row="showIncidentEditSheet"
          >
            <template #item.project.name="{ item, value }">
              <v-chip size="small" :color="item.project.color">
                {{ value }}
              </v-chip>
            </template>
            <template #item.incident_severity.name="{ value }">
              <incident-severity :severity="value" />
            </template>
            <template #item.incident_priority.name="{ value }">
              <incident-priority :priority="value" />
            </template>
            <template #item.status="{ item, value }">
              <incident-status
                :status="value"
                :id="item.id"
                :allowSelfJoin="item.project.allow_self_join"
              />
            </template>
            <template #item.incident_costs="{ value }">
              <incident-cost-card :incident-costs="value" />
            </template>
            <template #item.commander="{ value }">
              <incident-participant :participant="value" />
            </template>
            <template #item.reported_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.closed_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu location="right" origin="overlap">
                <template #activator="{ props }">
                  <v-btn icon variant="text" v-bind="props">
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
                  <v-list-item
                    @click="showRun({ type: 'incident', data: item })"
                    :disabled="item.status == 'Closed'"
                  >
                    <v-list-item-title>Run Workflow</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="showDeleteDialog(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
    <bulk-edit-sheet />
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"
import BulkEditSheet from "@/incident/BulkEditSheet.vue"
import DeleteDialog from "@/incident/DeleteDialog.vue"
import IncidentCostCard from "@/incident_cost/IncidentCostCard.vue"
import IncidentParticipant from "@/incident/Participant.vue"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentSeverity from "@/incident/severity/IncidentSeverity.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"
import NewSheet from "@/incident/NewSheet.vue"
import ReportDialog from "@/incident/ReportDialog.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/incident/TableExportDialog.vue"
import TableFilterDialog from "@/incident/TableFilterDialog.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"

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
    TableExportDialog,
    TableFilterDialog,
    WorkflowRunModal,
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
        { title: "Name", key: "name", align: "left", width: "10%" },
        { title: "Title", key: "title", sortable: false },
        { title: "Status", key: "status" },
        { title: "Type", key: "incident_type.name" },
        { title: "Severity", key: "incident_severity.name", width: "10%" },
        { title: "Priority", key: "incident_priority.name", width: "10%" },
        { title: "Project", key: "project.name", sortable: true },
        { title: "Commander", key: "commander", sortable: false },
        { title: "Cost", key: "incident_costs", sortable: false },
        { title: "Reported At", key: "reported_at" },
        { title: "Closed At", key: "closed_at" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("incident", [
      "table.loading",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.commander",
      "table.options.filters.participant",
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
      "current_user_role",
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
    ...mapActions("incident", ["getAll", "showNewSheet", "showDeleteDialog", "showReportDialog"]),
    ...mapActions("workflow", ["showRun"]),
    showIncidentEditSheet(e, { item }) {
      this.$router.push({ name: "IncidentTableEdit", params: { name: item.name } })
    },

    userAdminOrAbove(role) {
      return ["Admin", "Owner", "Manager"].includes(role)
    },
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
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }
    if (this.filters.commander) {
      this.filters.participant = this.filters.commander
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
        vm.commander,
        vm.participant,
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
