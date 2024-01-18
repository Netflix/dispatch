<template>
  <new-edit-dialog />
  <attorney-edit-form />
  <delete-dialog />
  <v-container fluid>
    <v-row no-gutters>
      <delete-dialog />
      <v-col>
        <div class="text-h5">Forms</div>
      </v-col>
      <v-spacer />
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
        <table-export-dialog />
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
            <template #item.created_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(item.created_at) }}</span>
                </template>
                <span>{{ formatDate(item.created_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.updated_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(item.updated_at) }}</span>
                </template>
                <span>{{ formatDate(item.updated_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.project="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.form_type="{ item }">
              <span v-if="item.form_type">{{ item.form_type.name }}</span>
            </template>
            <template #item.creator="{ item }">
              <participant v-if="item.creator" :participant="convertToParticipant(item.creator)" />
              <span v-else>(anonymous)</span>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu location="right" origin="overlap">
                <template #activator="{ props }">
                  <v-btn icon variant="text" v-bind="props">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="editShow(item)">
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="attorneyEditShow(item)">
                    <v-list-item-title>Attorney Review</v-list-item-title>
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
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import NewEditDialog from "@/forms/EditForm.vue"
import AttorneyEditForm from "./AttorneyEditForm.vue"
import DeleteDialog from "@/forms/DeleteDialog.vue"
import Participant from "@/incident/Participant.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/task/TableExportDialog.vue"
import TableFilterDialog from "@/forms/table/TableFilterDialog.vue"

export default {
  name: "FormsTable",

  components: {
    DeleteDialog,
    NewEditDialog,
    Participant,
    TableExportDialog,
    TableFilterDialog,
    AttorneyEditForm,
  },

  data() {
    return {
      headers: [
        { title: "Project", value: "project" },
        { title: "Incident Name", value: "incident.name" },
        { title: "Type", value: "form_type" },
        { title: "Status", value: "status" },
        { title: "Creator", value: "creator" },
        { title: "Created At", value: "created_at" },
        { title: "Updated At", value: "updated_at" },
        { title: "Attorney Status", value: "attorney_status" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("forms_table", [
      "table.loading",
      "table.options.descending",
      "table.options.filters.project",
      "table.options.filters.forms_type",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
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
    ...mapActions("forms_table", ["getAll"]),
    ...mapActions("forms", [
      "editShow",
      "showDeleteDialog",
      "attorneyEditShow",
      "attorneyEditShowById",
    ]),
    convertToParticipant(individual) {
      return {
        individual: {
          name: individual.name,
          email: individual.email,
        },
      }
    },
  },

  watch: {
    $route: {
      immediate: true,
      handler: function (newVal) {
        this.showAttorneyEdit = newVal.meta && newVal.meta.showAttorneyEdit
        if (this.$route.params.id && this.showAttorneyEdit) {
          this.attorneyEditShowById(this.$route.params.id)
        }
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
        vm.q,
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.project,
        vm.status,
        vm.forms_type,
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
