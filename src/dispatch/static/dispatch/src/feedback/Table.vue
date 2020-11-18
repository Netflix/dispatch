<template>
  <v-layout wrap>
    <!-- <new&#45;edit&#45;sheet /> -->
    <delete-dialog />
    <div class="headline">Feedback</div>
    <v-spacer />
    <table-filter-dialog />
    <!-- <v&#45;btn color="primary" dark class="ml&#45;2" @click="createEditShow()">New</v&#45;btn> -->
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
              <template v-slot:item.participant="{ item }">
                <v-chip
                  v-if="item.participant"
                  class="ma-2"
                  pill
                  small
                  :href="item.participant.individual.weblink"
                >
                  {{ item.participant.individual.name }}
                </v-chip>
                <v-chip v-else class="ma-2" pill small>
                  Anonymous
                </v-chip>
              </template>
              <template v-slot:item.created_at="{ item }">{{
                item.created_at | formatDate
              }}</template>
              <template v-slot:item.data-table-actions="{ item }">
                <v-menu bottom left>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <!-- <v&#45;list&#45;item @click="createEditShow(item)"> -->
                    <!--   <v&#45;list&#45;item&#45;title>Edit</v&#45;list&#45;item&#45;title> -->
                    <!-- </v&#45;list&#45;item> -->
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
// import NewEditSheet from "@/feedback/NewEditSheet.vue"
import TableFilterDialog from "@/feedback/TableFilterDialog.vue"
export default {
  name: "FeedbackTable",

  components: {
    TableFilterDialog,
    DeleteDialog
    // NewEditSheet
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
        { text: "", value: "data-table-actions", sortable: false, align: "end" }
      ]
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
      vm => [
        vm.q,
        vm.itemsPerPage,
        vm.sortBy,
        vm.descending,
        vm.incident,
        vm.rating,
        vm.feedback,
        vm.participant
      ],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("feedback", ["getAll", "removeShow"])
    // ...mapActions("feedback", ["getAll", "createEditShow", "removeShow"])
  }
}
</script>
