<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <div class="headline">Tasks</div>
    <v-spacer />
    <table-filter-dialog />
    <!--<v-btn color="primary" dark class="mb-2" @click="createEditShow()">New</v-btn>-->
    <v-flex xs12>
      <v-layout column>
        <v-flex>
          <v-card>
            <v-card-title>
              <v-text-field
                v-model="q"
                append-icon="search"
                label="Search"
                single-line
                hide-details
                clearable
                :loading="loading"
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
            >
              <template v-slot:item.creator="{ item }">
                <v-chip class="ma-2" pill small :href="item.creator.individual.weblink">
                  {{ item.creator.individual.email }}
                </v-chip>
              </template>
              <template v-slot:item.tickets="{ item }">
                <a
                  v-for="ticket in item.tickets"
                  :key="ticket.weblink"
                  :href="ticket.weblink"
                  target="_blank"
                  style="text-decoration: none;"
                >
                  Ticket
                  <v-icon small>open_in_new</v-icon>
                </a>
              </template>
              <template v-slot:item.assignees="{ item }">
                <v-chip
                  v-for="assignee in item.assignees"
                  :key="assignee.id"
                  class="ma-2"
                  pill
                  small
                  :href="assignee.individual.weblink"
                >
                  {{ assignee.individual.name }}
                </v-chip>
              </template>
              <template v-slot:item.resolve_by="{ item }">{{
                item.resolve_by | formatDate
              }}</template>
              <template v-slot:item.created_at="{ item }">{{
                item.created_at | formatDate
              }}</template>
              <template v-slot:item.resolved_at="{ item }">{{
                item.resolved_at | formatDate
              }}</template>
              <template v-slot:item.source="{ item }">
                <a :href="item.weblink" target="_blank" style="text-decoration: none;">
                  {{ item.source }}
                  <v-icon small>open_in_new</v-icon>
                </a>
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
import DeleteDialog from "@/task/DeleteDialog.vue"
import NewEditSheet from "@/task/NewEditSheet.vue"
import TableFilterDialog from "@/task/TableFilterDialog.vue"
export default {
  name: "TaskTable",

  components: {
    TableFilterDialog,
    DeleteDialog,
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Incident Name", value: "incident.name", sortable: false },
        { text: "Incident Priority", value: "incident.incident_priority.name", sortable: false },
        { text: "Incident Type", value: "incident.incident_type.name", sortable: false },
        { text: "Status", value: "status", sortable: true },
        { text: "Creator", value: "creator", sortable: true },
        { text: "Assignees", value: "assignees", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Source", value: "source", sortable: true },
        { text: "Tickets", value: "tickets", sortable: false },
        { text: "Due By", value: "resolve_by" },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "Resolved At", value: "resolved_at", sortable: true }
        //{ text: "Actions", value: "actions", sortable: false }
      ]
    }
  },

  computed: {
    ...mapFields("task", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.creator",
      "table.options.filters.assignee",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.loading",
      "table.rows.items",
      "table.rows.total"
    ])
  },

  mounted() {
    this.getAll({})

    this.$watch(
      vm => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      vm => [
        vm.q,
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.creator,
        vm.assignee,
        vm.incident_type,
        vm.incident_priority,
        vm.status
      ],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("task", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
