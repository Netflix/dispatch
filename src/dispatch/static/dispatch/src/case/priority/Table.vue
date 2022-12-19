<template>
  <v-container fluid>
    <new-edit-sheet />
    <v-row no-gutters>
      <v-col>
        <v-alert dismissible icon="mdi-school" prominent text type="info">
          Priorities add another dimension to Dispatch's case categorization. They also allow for
          some configurability.
        </v-alert>
      </v-col>
    </v-row>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col class="text-right">
        <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
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
            <template v-slot:item.page_assignee="{ item }">
              <v-simple-checkbox v-model="item.page_assignee" disabled />
            </template>
            <template v-slot:item.default="{ item }">
              <v-simple-checkbox v-model="item.default" disabled />
            </template>
            <template v-slot:item.enabled="{ item }">
              <v-simple-checkbox v-model="item.enabled" disabled />
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
                    <v-list-item-title>View / Edit</v-list-item-title>
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

import NewEditSheet from "@/case/priority/NewEditSheet.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"

export default {
  name: "CasePriorityTable",

  components: {
    NewEditSheet,
    SettingsBreadcrumbs,
  },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Page Assignee", value: "page_assignee", sortable: true },
        { text: "Default", value: "default", sortable: true },
        { text: "Enabled", value: "enabled", sortable: true },
        { text: "View Order", value: "view_order", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("case_priority", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
    ]),
    ...mapFields("route", ["query", "params"]),
  },

  created() {
    this.project = [{ name: this.query.project }]

    this.getAll()

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project],
      () => {
        this.page = 1
        this.$router.push({ query: { project: this.project[0].name } })
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("case_priority", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
