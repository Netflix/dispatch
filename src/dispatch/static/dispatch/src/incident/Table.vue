<template>
  <v-layout wrap>
    <new-edit-sheet />
    <!--<delete-dialog />-->
    <div class="headline">Incidents</div>
    <v-spacer />
    <v-btn color="primary" dark @click="createEditShow()">New</v-btn>
    <v-menu v-model="filterMenu" :close-on-content-click="false" :nudge-width="300" offset-y>
      <template v-slot:activator="{ on }">
        <v-badge :value="numFilters" bordered overlap :content="numFilters">
          <v-btn class="ml-2" color="secondary" dark v-on="on">Filters</v-btn>
        </v-badge>
      </template>

      <v-card>
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <individual-combobox v-model="commanders" label="Commanders"></individual-combobox>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <individual-combobox v-model="reporters" label="Reporters"></individual-combobox>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <incident-type-combobox v-model="incidentTypes" />
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <incident-priority-combobox v-model="incidentPriorities" />
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <incident-status-multi-select v-model="incidentStatuses" />
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
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
              <template v-slot:item.actions="{ item }">
                <v-icon small class="mr-2" @click="createEditShow(item)">edit</v-icon>
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
import NewEditSheet from "@/incident/NewEditSheet.vue"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
import IndividualCombobox from "@/individual/IndividualCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"

export default {
  name: "IncidentTable",

  components: {
    // DeleteDialog
    NewEditSheet,
    IndividualCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    IncidentStatusMultiSelect
  },
  data() {
    return {
      filterMenu: false,
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
        { text: "Reported At", value: "reported_at" },
        { text: "Actions", value: "actions", sortable: false, align: "right", width: "5%" }
      ]
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.filters.commanders",
      "table.options.filters.reporters",
      "table.options.filters.incidentTypes",
      "table.options.filters.incidentPriorities",
      "table.options.filters.incidentStatuses",
      "table.options.descending",
      "table.loading",
      "table.rows.items",
      "table.rows.total"
    ]),
    numFilters: function() {
      return _.sum([
        this.reporters.length,
        this.commanders.length,
        this.incidentTypes.length,
        this.incidentPriorities.length,
        this.incidentStatuses.length
      ])
    }
  },

  mounted() {
    this.getAll({})

    this.$watch(
      vm => [vm.q, vm.page, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("incident", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
