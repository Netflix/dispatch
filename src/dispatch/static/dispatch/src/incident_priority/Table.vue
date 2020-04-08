<template>
  <v-layout wrap>
    <new-edit-sheet />
    <div class="headline">Incident Priorities</div>
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
              <template v-slot:item.page_commander="{ item }">{{
                item.page_commander | capitalize
              }}</template>
              <template v-slot:item.actions="{ item }">
                <v-icon small class="mr-2" @click="createEditShow(item)">edit</v-icon>
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
import NewEditSheet from "@/incident_priority/NewEditSheet.vue"
export default {
  name: "IncidentPriorityTable",

  components: {
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Description", value: "description", sortable: false },
        { text: "View Order", value: "view_order", sortable: true },
        { text: "Page Commander", value: "page_commander", sortable: true },
        { text: "Actions", value: "actions", sortable: false }
      ]
    }
  },

  computed: {
    ...mapFields("incident_priority", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.loading",
      "table.rows.items",
      "table.rows.total"
    ])
  },

  mounted() {
    this.getAll({})

    this.$watch(
      vm => [vm.q, vm.page, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        console.log("foo")
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("incident_priority", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
