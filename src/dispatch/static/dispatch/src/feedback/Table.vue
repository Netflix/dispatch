<template>
  <v-layout wrap>
    <delete-dialog />
    <div class="headline">Feedback</div>
    <v-spacer />
    <table-filter-dialog />
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
              <template v-slot:item.participant="{ item }">
                <participant :participant="item.participant" />
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
import DeleteDialog from "@/feedback/DeleteDialog.vue"
import TableFilterDialog from "@/feedback/TableFilterDialog.vue"
import Participant from "@/incident/Participant.vue"
export default {
  name: "FeedbackTable",

  components: {
    TableFilterDialog,
    DeleteDialog,
    Participant,
  },
  data() {
    return {
      headers: [
        { text: "Incident", value: "incident.name", sortable: false },
        { text: "Title", value: "incident.title", sortable: false },
        { text: "Rating", value: "rating", sortable: true },
        { text: "Feedback", value: "feedback", sortable: true },
        { text: "Participant", value: "participant", sortable: true },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("feedback", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.incident",
      "table.options.filters.rating",
      "table.options.filters.feedback",
      "table.options.filters.participant",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
    ]),
    ...mapFields("route", ["query"]),
  },

  mounted() {
    if (this.query.project) {
      this.project = [{ name: this.query.project }]
    }
    this.getAll({})

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [
        vm.q,
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.incident,
        vm.rating,
        vm.feedback,
        vm.participant,
      ],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("feedback", ["getAll", "removeShow"]),
  },
}
</script>
