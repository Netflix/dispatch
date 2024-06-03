<template>
  <v-container fluid>
    <v-row no-gutters>
      <new-edit-sheet />
      <delete-dialog />
      <v-col>
        <div class="text-h5">Tasks</div>
      </v-col>
      <v-spacer />
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
        <table-export-dialog />
        <v-btn color="info" class="ml-2" @click="createEditShow()"> New </v-btn>
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
            v-model:sort-by="sortBy"
            v-model:sort-desc="descending"
            v-model="selected"
            :loading="loading"
            loading-text="Loading... Please wait"
            show-select
            return-object
          >
            <template #item.description="{ item }">
              <div class="text-truncate" style="max-width: 400px">
                {{ item.description }}
              </div>
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.incident_priority.name="{ item }">
              <incident-priority :priority="item.incident.incident_priority.name" />
            </template>
            <template #item.creator.individual_contact.name="{ item }">
              <participant :participant="item.creator" />
            </template>
            <template #item.owner.individual_contact.name="{ item }">
              <participant :participant="item.owner" />
            </template>
            <template #item.incident_type.name="{ item }">
              {{ item.incident.incident_type.name }}
            </template>
            <template #item.assignees="{ item }">
              <participant
                v-for="assignee in item.assignees"
                :key="assignee.id"
                :participant="assignee"
              />
            </template>
            <template #item.resolve_by="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(item.resolve_by) }}</span>
                </template>
                <span>{{ formatDate(item.resolve_by) }}</span>
              </v-tooltip>
            </template>
            <template #item.created_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(item.created_at) }}</span>
                </template>
                <span>{{ formatDate(item.created_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.resolved_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(item.resolved_at) }}</span>
                </template>
                <span>{{ formatDate(item.resolved_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.source="{ item }">
              <a :href="item.weblink" target="_blank" style="text-decoration: none">
                {{ item.source }}
                <v-icon size="small">mdi-open-in-new</v-icon>
              </a>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu location="right" origin="overlap">
                <template #activator="{ props }">
                  <v-btn icon variant="text" v-bind="props">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="createEditShow(item)">
                    <v-list-item-title>View / Edit</v-list-item-title>
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

import BulkEditSheet from "@/task/BulkEditSheet.vue"
import DeleteDialog from "@/task/DeleteDialog.vue"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import NewEditSheet from "@/task/NewEditSheet.vue"
import Participant from "@/incident/Participant.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/task/TableExportDialog.vue"
import TableFilterDialog from "@/task/TableFilterDialog.vue"

export default {
  name: "TaskTable",

  components: {
    BulkEditSheet,
    DeleteDialog,
    IncidentPriority,
    NewEditSheet,
    Participant,
    TableExportDialog,
    TableFilterDialog,
  },

  data() {
    return {
      headers: [
        { title: "Incident Name", value: "incident.name", sortable: true },
        { title: "Incident Priority", value: "incident_priority.name", sortable: true },
        { title: "Incident Type", value: "incident_type.name", sortable: true },
        { title: "Status", value: "status", sortable: true },
        { title: "Creator", value: "creator.individual_contact.name", sortable: false },
        { title: "Owner", value: "owner.individual_contact.name", sortable: false },
        { title: "Assignees", value: "assignees", sortable: false },
        { title: "Description", value: "description", sortable: false },
        { title: "Source", value: "source", sortable: true },
        { title: "Project", value: "project.name", sortable: false },
        { title: "Due By", value: "resolve_by", sortable: true },
        { title: "Created At", value: "created_at", sortable: true },
        { title: "Resolved At", value: "resolved_at", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("task", [
      "table.options",
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.creator",
      "table.options.filters.assignee",
      "table.options.filters.incident",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
      "table.rows.selected",
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
    ...mapActions("task", ["getAll", "createEditShow", "removeShow"]),
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
        vm.q,
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.project,
        vm.incident,
        vm.incident_type,
        vm.incident_priority,
        vm.status,
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
