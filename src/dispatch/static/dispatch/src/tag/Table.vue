<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <div class="headline">Tags</div>
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
              <template v-slot:item.discoverable="{ item }">
                <v-simple-checkbox v-model="item.discoverable" disabled></v-simple-checkbox>
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
import DeleteDialog from "@/tag/DeleteDialog.vue"
import NewEditSheet from "@/tag/NewEditSheet.vue"
export default {
  name: "TagTable",

  components: {
    DeleteDialog,
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: true },
        { text: "Type", value: "type", sortable: true },
        { text: "Source", value: "source", sortable: true },
        { text: "Discoverable", value: "discoverable", sortable: true },
        { text: "Actions", value: "actions", sortable: false }
      ]
    }
  },

  computed: {
    ...mapFields("tag", [
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
    ...mapActions("tag", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
