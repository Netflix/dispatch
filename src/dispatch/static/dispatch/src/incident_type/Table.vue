<template>
  <v-layout wrap>
    <new-edit-sheet />
    <v-row align="center" justify="space-between">
      <v-col class="grow">
        <settings-breadcrumbs v-model="project" />
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
import NewEditSheet from "@/incident_type/NewEditSheet.vue"

export default {
  name: "IncidentTypeTable",

  components: {
    NewEditSheet,
    SettingsBreadcrumbs,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Visibility", value: "visibility", sortable: false },
        { text: "Commander Service", value: "commander_service.name", sortable: false },
        { text: "Liaison Service", value: "liaison_service.name", sortable: false },
        { text: "Incident Document", value: "incident_template_document.name", sortable: false },
        { text: "Enabled", value: "enabled", sortable: true },
        { text: "Default", value: "default", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("incident_type", [
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
    ...mapFields("route", ["query"]),
  },

  created() {
    this.project = [{ name: this.query.project }]

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

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
    ...mapActions("incident_type", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
