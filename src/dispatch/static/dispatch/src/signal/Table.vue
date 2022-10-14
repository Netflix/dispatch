<template>
  <v-container fluid>
    <new-edit-dialog />
    <delete-dialog />
    <v-row no-gutters>
      <v-col>
        <v-alert dismissible icon="mdi-school" prominent text type="info"
          >Signal definitions determine how a signal is processed. Allowing you to map case types,
          supression and duplication rules for each signal.
        </v-alert>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <div class="headline">Signal Definitions</div>
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
            <template v-slot:item.status="{ item }">
              <case-status :status="item.status" :id="item.id" />
            </template>
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template v-slot:item.case_type.name="{ item }">
              <v-chip small color="info" text-color="white">
                {{ item.case_type.name }}
              </v-chip>
            </template>
            <template v-slot:item.case_priority.name="{ item }">
              <v-chip small :color="item.case_priority.color" text-color="white">
                {{ item.case_priority.name }}
              </v-chip>
            </template>
            <template v-slot:item.external_url="{ item }">
              <v-btn v-if="item.external_url" :href="item.external_url" target="_blank" icon>
                <v-icon>mdi-open-in-new</v-icon>
              </v-btn>
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

import RouterUtils from "@/router/utils"
import NewEditDialog from "@/signal/NewEditSheet.vue"
import DeleteDialog from "@/signal/DeleteDialog.vue"

export default {
  name: "SignalTable",

  components: { NewEditDialog, DeleteDialog },

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
        { text: "Variant", value: "variant", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Owner", value: "owner" },
        { text: "Case Type", value: "case_type.name" },
        { text: "Case Priority", value: "case_priority.name" },
        { text: "", value: "external_url", sortable: false },
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
    ...mapActions("signal", ["getAll", "createEditShow", "removeShow"]),
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
