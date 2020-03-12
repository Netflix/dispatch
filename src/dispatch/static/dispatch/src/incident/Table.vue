<template>
  <v-layout wrap>
    <new-edit-sheet />
    <!--<delete-dialog />-->
    <div class="headline">Incidents</div>
    <v-spacer />
    <v-btn color="primary" dark class="mb-2" @click="createEditShow()">New</v-btn>
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
              <template v-slot:item.created_at="{ item }">
                {{ item.reported_at | formatDate }}
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
// import DeleteDialog from "@/incident/DeleteDialog.vue"
import NewEditSheet from "@/incident/NewEditSheet.vue"
export default {
  name: "IncidentTable",

  components: {
    // DeleteDialog
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Id", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", width: "10%" },
        { text: "Type", value: "incident_type.name" },
        { text: "Priority", value: "incident_priority.name", width: "10%" },
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
      "table.options.descending",
      "table.loading",
      "table.rows.items",
      "table.rows.total"
    ])
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
