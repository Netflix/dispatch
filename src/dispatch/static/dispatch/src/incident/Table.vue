<template>
  <v-layout wrap>
    <edit-sheet />
    <new-sheet />
    <!--<delete-dialog />-->
    <div class="headline">Incidents</div>
    <v-spacer />
    <v-dialog v-model="filterDialog" max-width="600px">
      <template v-slot:activator="{ on }">
        <v-badge :value="numFilters" bordered overlap :content="numFilters">
          <v-btn color="secondary" dark v-on="on">Filter Columns</v-btn>
        </v-badge>
      </template>
      <v-card>
        <v-card-title>
          <span class="headline">Column Filters</span>
        </v-card-title>
        <v-list dense>
          <!--
          <v-list-item>
            <v-list-item-content>
              <individual-combobox v-model="commander" label="Commanders"></individual-combobox>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <individual-combobox v-model="reporter" label="Reporters"></individual-combobox>
            </v-list-item-content>
          </v-list-item>
          -->
          <v-list-item>
            <v-list-item-content>
              <incident-type-combobox v-model="incident_type" />
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <incident-priority-combobox v-model="incident_priority" />
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <incident-status-multi-select v-model="status" />
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-dialog>
    <v-btn color="primary" dark class="ml-2" @click="showNewSheet()">New</v-btn>
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
              @click:row="showEditSheet"
              loading-text="Loading... Please wait"
            >
              <template v-slot:item.cost="{ item }">{{ item.cost | toUSD }}</template>
              <template v-slot:item.commander="{ item }">
                <div v-if="item.commander">
                  <div v-if="item.commander.name">{{ item.commander.name }}</div>
                  <div v-else>{{ item.commander.email }}</div>
                </div>
              </template>
              <template v-slot:item.reporter="{ item }">
                <div v-if="item.reporter">
                  <div v-if="item.reporter.name">{{ item.reporter.name }}</div>
                  <div v-else>{{ item.reporter.email }}</div>
                </div>
              </template>
              <template v-slot:item.reported_at="{ item }">{{
                item.reported_at | formatDate
              }}</template>
            </v-data-table>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import _ from "lodash"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
// import DeleteDialog from "@/incident/DeleteDialog.vue"
import EditSheet from "@/incident/EditSheet.vue"
import NewSheet from "@/incident/NewSheet.vue"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
// import IndividualCombobox from "@/individual/IndividualCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"

export default {
  name: "IncidentTable",

  components: {
    // DeleteDialog
    EditSheet,
    NewSheet,
    // IndividualCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    IncidentStatusMultiSelect
  },

  props: ["name"],

  data() {
    return {
      filterDialog: false,
      headers: [
        { text: "Id", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", width: "10%" },
        { text: "Visibility", value: "visibility", width: "10%" },
        { text: "Type", value: "incident_type.name" },
        { text: "Priority", value: "incident_priority.name", width: "10%" },
        { text: "Cost", value: "cost" },
        { text: "Commander", value: "commander" },
        { text: "Reporter", value: "reporter" },
        { text: "Reported At", value: "reported_at" }
      ]
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
      "table.options.descending",
      "table.loading",
      "table.rows.items",
      "table.rows.total"
    ]),
    numFilters: function() {
      return _.sum([
        this.reporter.length,
        this.commander.length,
        this.incident_type.length,
        this.incident_priority.length,
        this.status.length
      ])
    }
  },

  mounted() {
    // process our props
    if (this.name) {
      this.q = this.name
    }
    this.getAll()

    this.$watch(
      vm => [
        vm.q,
        vm.page,
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.commander,
        vm.reporter,
        vm.incident_type,
        vm.incident_priority,
        vm.status
      ],
      () => {
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("incident", ["getAll", "showNewSheet", "showEditSheet", "removeShow"])
  }
}
</script>
