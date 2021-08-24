<template>
  <v-container>
    <runbook-new-edit-sheet />
    <delete-dialog />
    <v-row align="center" justify="space-between" no-gutters>
      <v-col class="grow">
        <settings-breadcrumbs v-model="project" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col v-for="document in runbookDocumentTypes" :key="document.resource_type">
        <v-card
          outlined
          elevation="0"
          @click.stop="createEditShow({ resource_type: document.resource_type })"
        >
          <div class="d-flex flex-no-wrap justify-space-between">
            <div>
              <v-card-title class="text-h5">{{ document.title }}</v-card-title>
              <v-card-subtitle>{{ document.description }}</v-card-subtitle>
            </div>
            <v-avatar class="ma-3" tile>
              <v-icon x-large>{{ document.icon }}</v-icon>
            </v-avatar>
          </div>
        </v-card>
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
            <template v-slot:item.resource_type="{ item }">
              {{ getResourceTitle(item.resource_type) }}
            </template>
            <template v-slot:item.evergreen="{ item }">
              <v-simple-checkbox v-model="item.evergreen" disabled />
            </template>
            <template v-slot:item.description="{ item }">
              {{ item.description }}
            </template>
            <template v-slot:item.name="{ item }">
              <a :href="item.weblink" target="_blank" style="text-decoration: none">
                {{ item.name }}
                <v-icon small>open_in_new</v-icon>
              </a>
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

import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"
import RunbookNewEditSheet from "@/document/runbook/RunbookNewEditSheet.vue"
import DeleteDialog from "@/document/runbook/DeleteDialog.vue"
import { runbookDocumentTypes } from "@/document/runbook/store.js"

export default {
  name: "RunbookConfiguration",

  components: {
    SettingsBreadcrumbs,
    RunbookNewEditSheet,
    DeleteDialog,
  },
  data() {
    return {
      runbookDocumentTypes: runbookDocumentTypes,
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Type", value: "resource_type", sortable: true },
        { text: "Evergreen", value: "evergreen", sortable: true, width: "10%" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  computed: {
    ...mapFields("runbook", [
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
    getResourceTitle(resource_type) {
      const found = runbookDocumentTypes.find((item) => {
        return item.resource_type === resource_type
      })
      return found ? found.title : ""
    },
    ...mapActions("runbook", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
