<template>
  <v-container>
    <new-edit-sheet />
    <v-row align="center" justify="space-between" no-gutters>
      <delete-dialog />
      <v-col>
        <div class="headline">Sources</div>
      </v-col>
      <v-col cols="2">
        <table-filter-dialog :projects="defaultUserProjects" />
        <v-btn color="info" class="ml-2" @click="createEditShow()"> New </v-btn>
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
            loading-text="Loading... Please wait"
          >
            <template v-slot:item.name="{ item }">
              <router-link
                :to="{
                  name: 'SourceDetail',
                  params: { name: item.name, tab: 'details' },
                }"
                ><b>{{ item.name }}</b></router-link
              >
            </template>
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template v-slot:item.source_status="{ item }">
              <span v-if="item.source_status">
                {{ item.source_status.name }}
              </span>
            </template>
            <template v-slot:item.source_data_format="{ item }">
              <v-chip v-if="item.source_data_format" small dark>
                {{ item.source_data_format.name }}
              </v-chip>
            </template>
            <template v-slot:item.source_type="{ item }">
              <span v-if="item.source_type">
                {{ item.source_type.name }}
              </span>
            </template>
            <template v-slot:item.owner="{ item }">
              <service-popover v-if="item.owner" :service="item.owner" />
            </template>
            <template v-slot:item.data_last_loaded_at="{ item }">
              {{ item.data_last_loaded_at | formatRelativeDate }}
            </template>
            <template v-slot:item.data-table-actions="{ item }">
              <v-menu bottom left>
                <template v-slot:activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="createEditShow(item)">
                    <v-list-item-title>Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="removeShow(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
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

import DeleteDialog from "@/data/source/DeleteDialog.vue"
import NewEditSheet from "@/data/source/NewEditSheet.vue"
import RouterUtils from "@/router/utils"
import ServicePopover from "@/service/ServicePopover.vue"
import TableFilterDialog from "@/data/source/TableFilterDialog.vue"

export default {
  name: "SourceTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    ServicePopover,
    TableFilterDialog,
  },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Project", value: "project.name", sortable: false },
        { text: "Environment", value: "source_environment.name", sortable: true },
        { text: "Owner", value: "owner" },
        { text: "Status", value: "source_status", sortable: true },
        { text: "Type", value: "source_type", sortable: true },
        { text: "Last Loaded", value: "data_last_loaded_at", sortable: true },
        {
          text: "",
          value: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
    }
  },

  computed: {
    ...mapFields("source", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.options.filters.project",
      "table.options.filters.source_environment",
      "table.options.filters.source_type",
      "table.options.filters.source_transport",
      "table.options.filters.source_data_format",
      "table.options.filters.source_status",
      "table.loading",
      "table.rows.items",
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
    ...mapActions("source", ["getAll", "createEditShow", "removeShow"]),
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
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.project,
        vm.source_data_format,
        vm.source_environment,
        vm.source_status,
        vm.source_transport,
        vm.source_type,
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
