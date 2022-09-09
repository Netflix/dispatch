<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col>
        <div class="headline">Signals</div>
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
            show-select
          >
            <template v-slot:item.source.name="{ item }">
              <v-chip v-if="item.source" small color="info" text-color="white">
                {{ item.source.name }}
              </v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <case-status :status="item.status" :id="item.id" />
            </template>
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template v-slot:item.created_at="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.created_at | formatDate }}</span>
              </v-tooltip>
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

import RouterUtils from "@/router/utils"

export default {
  name: "SignalTable",

  components: {},

  props: {
    name: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Source", value: "source.name", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Created At", value: "created_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  computed: {
    ...mapFields("signal", [
      "table.loading",
      "table.options.descending",
      "table.options.filters",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.total",
    ]),
    ...mapFields("route", ["query"]),
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
    ...mapActions("signal", ["getAll"]),
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
      (vm) => [vm.q, vm.sortBy, vm.itemsPerPage, vm.descending, vm.created_at, vm.project],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAll()
      }
    )
  },
}
</script>
