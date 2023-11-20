<template>
  <v-container fluid>
    <new-edit-sheet />
    <v-row align="center" justify="space-between" no-gutters>
      <delete-dialog />
      <v-col>
        <div class="text-h5">Queries</div>
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
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
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

import DeleteDialog from "@/data/query/DeleteDialog.vue"
import NewEditSheet from "@/data/query/NewEditSheet.vue"
import RouterUtils from "@/router/utils"
import TableFilterDialog from "@/data/query/TableFilterDialog.vue"

export default {
  name: "QueryTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    TableFilterDialog,
  },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Project", value: "project.name", sortable: false },
        { title: "Description", value: "description", sortable: false },
        { title: "Language", value: "language", sortable: true },
        {
          title: "",
          key: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
    }
  },

  computed: {
    ...mapFields("query", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.options.filters.project",
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
    ...mapActions("query", ["getAll", "createEditShow", "removeShow"]),
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
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project, vm.tag, vm.tag_type],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAll()
      }
    )
  },
}
</script>
