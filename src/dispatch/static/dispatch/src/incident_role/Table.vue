<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <v-container>
      <v-row align="center" justify="space-between">
        <v-col class="grow">
          <settings-breadcrumbs v-model="project" />
        </v-col>
      </v-row>
      <v-row>
        <v-col v-for="incidentRole in incidentRoleTypes" :key="incidentRole.type">
          <v-card outlined elevation="0" @click.stop="createEditShow({ type: incidentRole.type })">
            <div class="d-flex flex-no-wrap justify-space-between">
              <div>
                <v-card-title class="text-h5">{{ incidentRole.title }}</v-card-title>
                <v-card-subtitle>{{ incidentRole.description }}</v-card-subtitle>
              </div>
              <v-avatar class="ma-3" tile>
                <v-icon x-large>{{ incidentRole.icon }}</v-icon>
              </v-avatar>
            </div>
          </v-card>
        </v-col>
      </v-row>
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
          <template v-slot:item.editable="{ item }">
            <v-simple-checkbox v-model="item.editable" disabled />
          </template>
          <template v-slot:item.details="{ item }">
            {{ item.details }}
          </template>
          <template v-slot:item.created_at="{ item }">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
              </template>
              <span>{{ item.created_at | formatDate }}</span>
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
    </v-container>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import DeleteDialog from "@/incident_cost_type/DeleteDialog.vue"
import NewEditSheet from "@/incident_cost_type/NewEditSheet.vue"
import { incidentRoleTypes } from "@/incident_role/store.js"

export default {
  name: "IncidentCostTypeTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    SettingsBreadcrumbs,
  },

  data() {
    return {
      incidentRoleTypes: incidentRoleTypes,
      headers: [
        { text: "Role", value: "role", sortable: false },
        { text: "Target", value: "target", sortable: false },
        { text: "Enabled", value: "enabled", sortable: false },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("incident_role", [
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
    ...mapActions("incident_role", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
