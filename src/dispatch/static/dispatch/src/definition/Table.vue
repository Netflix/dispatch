<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <div class="headline">
      Definitions
    </div>
    <v-spacer />
    <v-btn color="primary" dark class="mb-2" @click="createEditShow()">
      New
    </v-btn>
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
              :items-per-page="itemsPerPage"
              :sort-by="sortBy"
              :sort-desc="descending"
              :loading="loading"
              loading-text="Loading... Please wait"
            >
              <template v-slot:item.data-table-actions="{ item }">
                <v-menu bottom left>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item @click="createEditShow(item)">
                      <v-list-item-title>Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="removeShow(item)">
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
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import DeleteDialog from "@/definition/DeleteDialog.vue"
import NewEditSheet from "@/definition/NewEditSheet.vue"
export default {
  name: "DefinitionTable",

  components: {
    DeleteDialog,
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Text", value: "text", sortable: false },
        { text: "", value: "data-table-actions", sortable: false, align: "end" }
      ]
    }
  },

  computed: {
    ...mapFields("definition", [
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
    ...mapActions("definition", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
