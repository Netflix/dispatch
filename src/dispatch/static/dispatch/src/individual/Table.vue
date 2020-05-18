<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <div class="headline">Individuals</div>
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
              <template v-slot:item.is_active="{ item }">
                <v-simple-checkbox v-model="item.is_active" disabled></v-simple-checkbox>
              </template>
              <template v-slot:item.is_external="{ item }">
                <v-simple-checkbox v-model="item.is_external" disabled></v-simple-checkbox>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-icon small class="mr-2" @click="createEditShow(item)">edit</v-icon>
                <v-icon small @click="removeShow(item)">delete</v-icon>
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
import DeleteDialog from "@/individual/DeleteDialog.vue"
import NewEditSheet from "@/individual/NewEditSheet.vue"
export default {
  name: "IndividualTable",

  components: {
    DeleteDialog,
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Email", value: "email", sortable: true },
        { text: "Company", value: "company", sortable: true },
        { text: "Active", value: "is_active", sortable: true },
        { text: "External", value: "is_external", sortable: true },
        { text: "Actions", value: "actions", sortable: false }
      ]
    }
  },

  computed: {
    ...mapFields("individual", [
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
      vm => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      vm => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("individual", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
