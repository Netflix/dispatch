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
        <div class="text-h5">Cases</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
        <table-export-dialog />
        <v-btn color="info" class="ml-2" @click="showNewSheet()"> New </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card>
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
            v-model="selected"
            loading-text="Loading... Please wait"
            show-select
            return-object
            @click:row="showCaseEditSheet"
          >
            <template #item.case_severity.name="{ value }">
              <case-severity :severity="value" />
            </template>
            <template #item.case_priority.name="{ value }">
              <case-priority :priority="value" />
            </template>
            <template #item.status="{ item }">
              <case-status :status="item.status" :id="item.id" />
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.assignee="{ value }">
              <case-participant :participant="value" />
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

import BulkEditSheet from "@/case/BulkEditSheet.vue"
import CaseParticipant from "@/case/Participant.vue"
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
    CaseParticipant,
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
        { title: "Name", value: "name", align: "left", width: "10%" },
        { title: "Title", value: "title", sortable: false },
        { title: "Status", value: "status" },
        { title: "Type", value: "case_type.name", sortable: true },
        { title: "Severity", value: "case_severity.name", sortable: true },
        { title: "Priority", value: "case_priority.name", sortable: true },
        { title: "Project", value: "project.name", sortable: true },
        { title: "Assignee", value: "assignee", sortable: true },
        { title: "Reported At", value: "reported_at" },
        { title: "Closed At", value: "closed_at" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
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
    showCaseEditSheet(item) {
      this.$router.push({ name: "CaseTableEdit", params: { name: item.name } })
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
