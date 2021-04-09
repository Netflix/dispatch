<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <div class="headline">Notifications</div>
    <v-spacer />
    <v-btn color="info" class="ml-2" @click="createEditShow()"> New </v-btn>
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
              loading-text="Loading... Please wait"
            >
              <template v-slot:item.filters="{ item }">
                <search-filter v-for="filter in item.filters" :key="filter.id" :filter="filter" />
              </template>
              <template v-slot:item.enabled="{ item }">
                <v-simple-checkbox v-model="item.enabled" disabled />
              </template>
              <template v-slot:item.created_at="{ item }">
                {{ item.created_at | formatDate }}
              </template>
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
import DeleteDialog from "@/notification/DeleteDialog.vue"
import NewEditSheet from "@/notification/NewEditSheet.vue"
import SearchFilter from "@/search/SearchFilter.vue"
export default {
  name: "NotificationTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    SearchFilter,
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Type", value: "type", sortable: false },
        { text: "Target", value: "target", sortable: false },
        { text: "Filters", value: "filters", sortable: false },
        { text: "Enabled", value: "enabled", sortable: false },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("notification", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
    ]),
    ...mapFields("route", ["query"]),
  },

  mounted() {
    this.project = [{ name: this.query.project }]

    this.getAll({})

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("notification", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
