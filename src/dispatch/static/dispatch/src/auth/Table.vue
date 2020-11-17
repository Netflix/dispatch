<template>
  <v-layout wrap>
    <new-edit-sheet />
    <div class="headline">Users</div>
    <v-spacer />
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
              @click:row="editShow"
            >
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
import NewEditSheet from "@/auth/editSheet.vue"
export default {
  name: "UserTable",

  components: {
    NewEditSheet
  },
  data() {
    return {
      headers: [
        { text: "Email", value: "email", sortable: true },
        { text: "Role", value: "role", sortable: true }
      ]
    }
  },

  computed: {
    ...mapFields("auth", [
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
    ...mapActions("auth", ["getAll", "editShow"])
  }
}
</script>
