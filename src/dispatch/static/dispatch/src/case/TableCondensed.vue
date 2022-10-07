<template>
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
    <v-card-text>
      <v-row dense>
        <v-col v-for="item in items" :key="item.id" cols="12">
          <v-card flat outlined class="mx-auto" tile>
            <v-app-bar flat dense>
              <v-toolbar-title>
                {{ item.name }}
              </v-toolbar-title>
              <v-spacer />
              <v-menu bottom left>
                <template v-slot:activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item
                    :to="{
                      name: 'CaseTableEdit',
                      params: { name: item.name },
                    }"
                  >
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    v-if="item.status == 'New' || item.status == 'Triage'"
                    @click="showEscalateDialog(item)"
                  >
                    <v-list-item-title>Escalate</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="showDeleteDialog(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </v-app-bar>
            <v-card-text>{{ item.description }} </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-pagination />
    </v-card-text>
  </v-card>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import RouterUtils from "@/router/utils"

export default {
  name: "CaseTableCondensed",

  components: {},

  props: {
    name: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      showEditSheet: false,
    }
  },

  computed: {
    ...mapFields("case_management", [
      "table.loading",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.assignee",
      "table.options.filters.case_priority",
      "table.options.filters.case_severity",
      "table.options.filters.case_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.selected",
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
    ...mapActions("case_management", [
      "getAll",
      "showNewSheet",
      "showDeleteDialog",
      "showEscalateDialog",
    ]),
  },

  watch: {
    $route: {
      immediate: true,
      handler: function (newVal) {
        this.showEditSheet = newVal.meta && newVal.meta.showEditSheet
      },
    },
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
      (vm) => [
        vm.case_priority,
        vm.case_severity,
        vm.case_type,
        vm.descending,
        vm.itemsPerPage,
        vm.project,
        vm.q,
        vm.reported_at.end,
        vm.reported_at.start,
        vm.sortBy,
        vm.status,
        vm.tag,
        vm.tag_type,
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
