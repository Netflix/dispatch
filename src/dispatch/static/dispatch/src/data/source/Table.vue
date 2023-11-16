<template>
  <v-container fluid>
    <new-edit-sheet />
    <v-row align="center" justify="space-between" no-gutters>
      <delete-dialog />
      <v-col>
        <div class="text-h5">Sources</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
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
            :loading="loading"
            loading-text="Loading... Please wait"
          >
            <template #item.name="{ item }">
              <router-link
                :to="{
                  name: 'SourceDetail',
                  params: { name: item.name, tab: 'details' },
                }"
              >
                <b>{{ item.name }}</b>
              </router-link>
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.source_status="{ item }">
              <span v-if="item.source_status">
                {{ item.source_status.name }}
              </span>
            </template>
            <template #item.source_data_format="{ item }">
              <v-chip v-if="item.source_data_format" size="small">
                {{ item.source_data_format.name }}
              </v-chip>
            </template>
            <template #item.source_type="{ item }">
              <span v-if="item.source_type">
                {{ item.source_type.name }}
              </span>
            </template>
            <template #item.owner="{ item }">
              <service-popover v-if="item.owner" :service="item.owner" />
            </template>
            <template #item.data_last_loaded_at="{ value }">
              {{ formatRelativeDate(value) }}
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
                    <v-list-item-title>Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="removeShow(item)">
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
import { formatRelativeDate } from "@/filters"

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
        { title: "Name", value: "name", sortable: true },
        { title: "Project", value: "project.name", sortable: false },
        { title: "Environment", value: "source_environment.name", sortable: true },
        { title: "Owner", value: "owner" },
        { title: "Status", value: "source_status", sortable: true },
        { title: "Type", value: "source_type", sortable: true },
        { title: "Last Loaded", value: "data_last_loaded_at", sortable: true },
        {
          title: "",
          key: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
    }
  },

  setup() {
    return { formatRelativeDate }
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
