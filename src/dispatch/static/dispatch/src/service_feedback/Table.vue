<template>
  <v-container fluid>
    <delete-dialog />
    <v-row no-gutters>
      <v-col>
        <div class="headline">Service feedback</div>
      </v-col>
    </v-row>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
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
            <template #item.created_at="{ item }">
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.created_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template #item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu bottom left>
                <template #activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
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

import DeleteDialog from "@/feedback/DeleteDialog.vue"
import Participant from "@/incident/Participant.vue"
import RouterUtils from "@/router/utils"

export default {
  name: "ServiceFeedbackTable",

  components: {
    DeleteDialog,
    Participant,
  },

  data() {
    return {
      headers: [
        { text: "Shift End At", value: "shift_end_at", sortable: true },
        { text: "Participant", value: "individual", sortable: true },
        { text: "After Hours", value: "hours", sortable: true },
        { text: "Rating", value: "rating", sortable: true },
        { text: "Feedback", value: "feedback", sortable: true },
        { text: "Project", value: "project.name", sortable: false },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("feedback", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.loading",
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
    ...mapActions("service-feedback", ["getAll", "removeShow"]),
  },

  created() {
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
        vm.incident,
        vm.rating,
        vm.feedback,
        vm.project,
        vm.participant,
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
