<template>
  <v-layout wrap>
    <div v-if="showEditSheet">
      <router-view></router-view>
    </div>
    <new-sheet />
    <delete-dialog />
    <report-dialog />
    <div class="headline">Incidents</div>
    <v-spacer />
    <table-filter-dialog />
    <table-export-dialog />
    <v-btn color="info" class="ml-2" @click="showNewSheet()">New</v-btn>
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
              v-model="selected"
              loading-text="Loading... Please wait"
              show-select
            >
              <template v-slot:item.incident_priority.name="{ item }">
                <incident-priority :priority="item.incident_priority.name" />
              </template>
              <template v-slot:item.status="{ item }">
                <incident-status :status="item.status" :id="item.id" />
              </template>
              <template v-slot:item.incident_costs="{ item }">
                <incident-cost
                  v-for="incident_cost in item.incident_costs"
                  :key="incident_cost.id"
                  :incident_cost="incident_cost"
                />
              </template>
              <template v-slot:item.commander="{ item }">
                <incident-participant :participant="item.commander" />
              </template>
              <template v-slot:item.reporter="{ item }">
                <incident-participant :participant="item.reporter" />
              </template>
              <template v-slot:item.reported_at="{ item }">{{
                item.reported_at | formatDate
              }}</template>
              <template v-slot:item.data-table-actions="{ item }">
                <v-menu bottom left>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item :to="`/incidents/${item.name}`">
                      <v-list-item-title>View / Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="showReportDialog(item)"
                      :disabled="item.status == 'Closed'"
                    >
                      <v-list-item-title>Create Report</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="showDeleteDialog(item)">
                      <v-list-item-title>Delete</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </template>
            </v-data-table>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
    <bulk-edit-sheet></bulk-edit-sheet>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import BulkEditSheet from "@/incident/BulkEditSheet.vue"
import DeleteDialog from "@/incident/DeleteDialog.vue"
import IncidentCost from "@/incident_cost/IncidentCost.vue"
import IncidentParticipant from "@/incident/Participant.vue"
import IncidentPriority from "@/incident/IncidentPriority.vue"
import IncidentStatus from "@/incident/IncidentStatus.vue"
import NewSheet from "@/incident/NewSheet.vue"
import ReportDialog from "@/incident/ReportDialog.vue"
import TableExportDialog from "@/incident/TableExportDialog.vue"
import TableFilterDialog from "@/incident/TableFilterDialog.vue"

export default {
  name: "IncidentTable",

  components: {
    BulkEditSheet,
    DeleteDialog,
    IncidentCost,
    IncidentParticipant,
    IncidentPriority,
    IncidentStatus,
    NewSheet,
    ReportDialog,
    TableExportDialog,
    TableFilterDialog
  },

  props: ["name"],

  data() {
    return {
      headers: [
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status" },
        { text: "Type", value: "incident_type.name" },
        { text: "Priority", value: "incident_priority.name", width: "10%" },
        { text: "Costs", value: "incident_costs" },
        { text: "Commander", value: "commander", sortable: false },
        { text: "Reported At", value: "reported_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" }
      ],
      showEditSheet: false
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.filters.commander",
      "table.options.filters.reporter",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.descending",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
      "table.rows.selected"
    ])
  },

  watch: {
    $route: {
      immediate: true,
      handler: function(newVal) {
        this.showEditSheet = newVal.meta && newVal.meta.showEditSheet
      }
    }
  },

  mounted() {
    this.getAll()

    this.$watch(
      vm => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      vm => [
        vm.q,
        vm.sortBy,
        vm.itemsPerPage,
        vm.descending,
        vm.commander,
        vm.reporter,
        vm.incident_type,
        vm.incident_priority,
        vm.status,
        vm.tag
      ],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("incident", ["getAll", "showNewSheet", "showDeleteDialog", "showReportDialog"])
  }
}
</script>
