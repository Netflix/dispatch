<template>
  <v-container>
    <new-edit-sheet />
    <delete-dialog />
    <v-row align="center" justify="space-between" no-gutters>
      <v-col>
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col cols="1">
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
            <template v-slot:item.is_active="{ item }">
              <v-simple-checkbox v-model="item.is_active" disabled />
            </template>
            <template v-slot:item.is_external="{ item }">
              <v-simple-checkbox v-model="item.is_external" disabled />
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
import DeleteDialog from "@/individual/DeleteDialog.vue"
import NewEditSheet from "@/individual/NewEditSheet.vue"

export default {
  name: "IndividualTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    SettingsBreadcrumbs,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Email", value: "email", sortable: true },
        { text: "Company", value: "company", sortable: true },
        { text: "Active", value: "is_active", sortable: true },
        { text: "External", value: "is_external", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("individual", [
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
    ...mapActions("individual", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
