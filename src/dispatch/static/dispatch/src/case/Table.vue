<template>
  <v-container>
    <div v-if="showEditSheet">
      <router-view />
    </div>
    <v-row no-gutters>
      <new-sheet />
      <delete-dialog />
      <v-col>
        <div class="headline">Cases</div>
      </v-col>
      <v-col cols="3">
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
            <template v-slot:item.source.name="{ item }">
              <v-chip small color="info" text-color="white">
                {{ item.source.name }}
              </v-chip>
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
import CaseStatus from "@/case/CaseStatus.vue"
import DeleteDialog from "@/case/DeleteDialog.vue"
import NewSheet from "@/case/NewSheet.vue"
import RouterUtils from "@/router/utils"

export default {
  name: "CaseTable",

  components: {
    BulkEditSheet,
    CaseStatus,
    DeleteDialog,
    NewSheet,
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
        { text: "Assignee", value: "assignee.email", sortable: true },
        { text: "Source", value: "source.name", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
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
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.source",
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
    ...mapActions("case_management", ["getAll", "showNewSheet", "showDeleteDialog"]),
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
        vm.q,
        vm.sortBy,
        vm.itemsPerPage,
        vm.descending,
        vm.reported_at.start,
        vm.reported_at.end,
        vm.project,
        vm.status,
        vm.tag_type,
        vm.tag,
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
