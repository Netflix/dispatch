<template>
  <v-layout wrap>
    <new-edit-sheet />
    <v-row align="center" justify="space-between">
      <v-col class="grow">
        <settings-breadcrumbs v-model="project" :organization="organization" />
      </v-col>
      <v-col class="shrink">
        <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
      </v-col>
    </v-row>
    <v-flex xs12>
      <v-layout column>
        <v-flex>
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
              <template v-slot:item.page_commander="{ item }">
                <v-simple-checkbox v-model="item.page_commander" disabled />
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
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import NewEditSheet from "@/incident_priority/NewEditSheet.vue"

export default {
  name: "IncidentPriorityTable",

  components: {
    NewEditSheet,
    SettingsBreadcrumbs,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Page Commander", value: "page_commander", sortable: true },
        { text: "Default", value: "default", sortable: true },
        { text: "Enabled", value: "enabled", sortable: true },
        { text: "Tactical Report Reminder", value: "tactical_report_reminder", sortable: true },
        { text: "Executive Report Reminder", value: "executive_report_reminder", sortable: true },
        { text: "View Order", value: "view_order", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("incident_priority", [
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
    ...mapActions("incident_priority", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
