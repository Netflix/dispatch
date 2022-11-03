<template>
  <v-container fluid>
    <div v-if="showEditSheet">
      <router-view />
    </div>
    <v-row no-gutters>
      <new-sheet />
      <workflow-run-modal />
      <escalate-dialog />
      <delete-dialog />
      <v-col>
        <div class="headline">Cases</div>
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
            v-model="selected"
            loading-text="Loading... Please wait"
            show-select
          >
            <template v-slot:item.case_severity.name="{ item }">
              <case-severity :severity="item.case_severity.name" />
            </template>
            <template v-slot:item.case_priority.name="{ item }">
              <case-priority :priority="item.case_priority.name" />
            </template>
            <template v-slot:item.status="{ item }">
              <case-status :status="item.status" :id="item.id" />
            </template>
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
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
                    :to="{
                      name: 'CaseTableEdit',
                      params: { name: item.name },
                    }"
                  >
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    @click="showRun({ type: 'case', data: item })"
                    :disabled="item.status == 'Escalated' || item.status == 'Closed'"
                  >
                    <v-list-item-title>Run Workflow</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    @click="showEscalateDialog(item)"
                    :disabled="item.status == 'Escalated' || item.status == 'Closed'"
                  >
                    <v-list-item-title>Escalate</v-list-item-title>
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

import BulkEditSheet from "@/case/BulkEditSheet.vue"
import CasePriority from "@/case/priority/CasePriority.vue"
import CaseSeverity from "@/case/severity/CaseSeverity.vue"
import CaseStatus from "@/case/CaseStatus.vue"
import DeleteDialog from "@/case/DeleteDialog.vue"
import EscalateDialog from "@/case/EscalateDialog.vue"
import NewSheet from "@/case/NewSheet.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/case/TableExportDialog.vue"
import TableFilterDialog from "@/case/TableFilterDialog.vue"

export default {
  name: "CaseTable",

  components: {
    BulkEditSheet,
    CasePriority,
    CaseSeverity,
    CaseStatus,
    DeleteDialog,
    EscalateDialog,
    NewSheet,
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
        { text: "Type", value: "case_type.name", sortable: true },
        { text: "Severity", value: "case_severity.name", sortable: true },
        { text: "Priority", value: "case_priority.name", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Assignee", value: "assignee.email", sortable: true },
        { text: "Reported At", value: "reported_at" },
        { text: "Closed At", value: "closed_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  computed: {
    ...mapFields("case_management", [
      "table.loading",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.assignee",
      "table.options.filters.case_priority",
      "table.options.filters.case_severity",
      "table.options.filters.case_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
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
    ...mapActions("workflow", ["showRun"]),
    ...mapActions("case_management", [
      "getAll",
      "showNewSheet",
      "showDeleteDialog",
      "showEscalateDialog",
    ]),
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
        vm.case_priority,
        vm.case_severity,
        vm.case_type,
        vm.descending,
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
