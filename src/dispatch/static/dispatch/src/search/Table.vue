<template>
  <v-container fluid>
    <!-- <new-edit-dialog /> -->
    <delete-dialog />
    <v-row no-gutters>
      <v-col>
        <v-alert dismissible icon="mdi-school" prominent text type="info">
          Search filters enable you to define under which conditions an individual, oncall service,
          or team need to be engage in an incident.
        </v-alert>
      </v-col>
    </v-row>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <!-- <v-col class="text-right"> -->
      <!--   <v-btn color="info" class="ml-2" @click="createEditShow()"> New </v-btn> -->
      <!-- </v-col> -->
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
            <template #[`item.individuals`]="{ item }">
              <v-chip small color="info" text-color="white">{{ item.individuals.length }}</v-chip>
            </template>
            <template #[`item.teams`]="{ item }">
              <v-chip small color="info" text-color="white">{{ item.teams.length }}</v-chip>
            </template>
            <template #[`item.services`]="{ item }">
              <v-chip small color="info" text-color="white">{{ item.services.length }}</v-chip>
            </template>
            <template #[`item.enabled`]="{ item }">
              <v-simple-checkbox v-model="item.enabled" disabled />
            </template>
            <template #[`item.created_at`]="{ item }">
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.created_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template #[`item.updated_at`]="{ item }">
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.updated_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.updated_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template #[`item.data-table-actions`]="{ item }">
              <v-menu bottom left>
                <template #activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <!-- <v-list-item @click="createEditShow(item)"> -->
                  <!--   <v-list-item-title>View / Edit</v-list-item-title> -->
                  <!-- </v-list-item> -->
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

import DeleteDialog from "@/search/DeleteDialog.vue"

export default {
  name: "SearchFilterTable",

  components: { DeleteDialog },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Description", value: "description", sortable: false },
        { text: "Individuals", value: "individuals" },
        { text: "Teams", value: "teams" },
        { text: "Services", value: "services" },
        { text: "Creator", value: "creator.email" },
        { text: "Created At", value: "created_at" },
        { text: "Updated At", value: "updated_at" },
        { text: "Enabled", value: "enabled" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  computed: {
    ...mapFields("search", [
      "table.loading",
      "table.options.descending",
      "table.options.filters.project",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.total",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("search", ["getAll", "createEditShow", "removeShow"]),
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
}
</script>
